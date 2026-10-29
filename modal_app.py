
import os
import modal

# 1. Initialize Modal App
app = modal.App("traceguard-threat-engine")

# 2. Persistent volume to cache Llama 3.1 weights permanently on cloud disk
hf_cache_vol = modal.Volume.from_name("hf-modal-cache", create_if_missing=True)

# 3. Define Debian environment with PyTorch and Transformers
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.4.0",
        "transformers==4.44.2",
        "accelerate==0.34.2"
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
    timeout=600,
    scaledown_window=300
)
class LlamaSynthesizer:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        token = os.environ.get("HF_TOKEN")
        if not token:
            print("[WARN] HF_TOKEN secret not detected, attempting unauthenticated fetch...")

        print("[*] Initializing Llama 3.1 8B Instruct model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            token=token,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        print("[✓] Model weights loaded into A10G VRAM.")

    @modal.method()
    def synthesize_threat(self, payload: dict, probe: bool = False) -> dict:
        import torch
        import json

        telemetry_str = json.dumps(payload, indent=2)

        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are TraceGuard, an autonomous DevSecOps threat correlation sentinel.
Analyze the provided telemetry: committer exposure, missing SPF/DMARC perimeter records, and repository metadata.
Calculate CVSS 3.1 score and risk severity.
Return ONLY valid JSON matching this schema:
{{
  "cvss_score": <float 0.0 to 10.0>,
  "risk_grade": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "attack_chain_summary": "<concise attack vector synthesis>",
  "vulnerabilities": [
    {{
      "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
      "finding": "<concise finding description>",
      "vector": "<CVSS vector string>",
      "remediation": "<actionable remediation guidance>"
    }}
  ]
}}
<|eot_id|><|start_header_id|>user<|end_header_id|>
Repository & Identity Telemetry:
{telemetry_str}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")

        probe_metrics = {"active": False}
        if probe:
            try:
                with torch.no_grad():
                    # Forward pass requesting hidden states across all layers
                    outputs = self.model(**inputs, output_hidden_states=True)
                    # Residual stream tensor at Layer 16 for the final prompt token
                    layer_16_state = outputs.hidden_states[16][0, -1, :].float()
                    norm_val = torch.norm(layer_16_state).item()

                    probe_metrics = {
                        "active": True,
                        "layer": 16,
                        "activation_norm": round(norm_val, 2),
                        "tamper_detected": norm_val > 55.0
                    }
            except Exception as e:
                probe_metrics = {"active": False, "error": str(e)}

        with torch.no_grad():
            output_tokens = self.model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(
            output_tokens[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        return {
            "raw_output": generated_text,
            "probe_metrics": probe_metrics
        }
