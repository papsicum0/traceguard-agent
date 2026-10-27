import os
import modal

# 1. Initialize the Modal App
app = modal.App("traceguard-threat-engine")

# 2. Persistent volume to cache Llama 3.1 weights permanently on cloud disk
hf_cache_vol = modal.Volume.from_name("hf-model-cache", create_if_missing=True)

# 3. Define the Debian environment with PyTorch and Transformers
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch>=2.1.0",
        "transformers>=4.43.0",
        "accelerate>=0.30.0"
    )
    .env({"HF_HUB_CACHE": "/root/cache"})
)

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# 4. Model inference class on NVIDIA A10G GPU
@app.cls(
    image=image,
    gpu="A10G",
    secrets=[modal.Secret.from_name("huggingface-secret")],
    volumes={"/root/cache": hf_cache_vol},
    timeout=600
)
class LlamaSynthesizer:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoTokenizer, pipeline

        token = os.environ.get("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN secret not found in container environment.")

        print("[*] Loading tokenizer and model weights into A10G memory...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            token=token,
            cache_dir="/root/cache"
        )
        self.pipeline = pipeline(
            "text-generation",
            model=MODEL_ID,
            tokenizer=self.tokenizer,
            model_kwargs={"torch_dtype": torch.bfloat16, "cache_dir": "/root/cache"},
            device_map="auto",
            token=token
        )
        
        # Persist downloaded files to volume so future runs don't re-download
        try:
            hf_cache_vol.commit()
        except Exception:
            pass

        print("[+] Meta Llama 3.1 8B successfully loaded.")

    @modal.method()
    def synthesize(self, telemetry_data: str) -> str:
        system_prompt = (
            "You are TraceGuard's autonomous DevSecOps threat engine. "
            "Analyze the provided reconnaissance telemetry (exposed commit metadata, git leaks, DNS posture). "
            "Synthesize correlated attack chains and output strictly valid JSON with this schema:\n"
            "{\n"
            '  "cvss_score": 6.5,\n'
            '  "risk_grade": "MEDIUM",\n'
            '  "attack_chain_summary": "Summary here",\n'
            '  "vulnerabilities": [\n'
            '    {\n'
            '      "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H",\n'
            '      "severity": "HIGH",\n'
            '      "finding": "Description of finding",\n'
            '      "remediation": "Exact remediation steps"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Telemetry Data:\n{telemetry_data}"}
        ]

        outputs = self.pipeline(
            messages,
            max_new_tokens=600,
            do_sample=True,
            temperature=0.1
        )
        return outputs[0]["generated_text"][-1]["content"]


# 5. Local test entrypoint for quick sanity checking
@app.local_entrypoint()
def main():
    synthesizer = LlamaSynthesizer()
    sample_recon = (
        "Commit Author: dev@internal-corp.net leaked in commit 9f8a12c. "
        "Missing DMARC and SPF TXT records on internal-corp.net domain."
    )
    print("\n--- Dispatching sample DevSecOps telemetry to cloud A10G ---")
    result = synthesizer.synthesize.remote(sample_recon)
    print("\n[Threat Intelligence Result]:\n")
    print(result)
