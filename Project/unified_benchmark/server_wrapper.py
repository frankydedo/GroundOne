import subprocess
import time
import requests
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

class ServerWrapper:
    def __init__(self, pipeline: str, model_id: str = None, adapter_path: str = None):
        """
        pipeline: 'lightning', 'llm', 'rizzo'
        """
        self.pipeline = pipeline
        self.model_id = model_id
        self.adapter_path = adapter_path
        self.processes = []
        self.log_files = []
        self.base_dir = "/Users/francescodedominicis/Desktop/THESIS/Project"
        os.makedirs(LOG_DIR, exist_ok=True)
        
    def start(self):
        print(f"\n🚀 Booting {self.pipeline} pipeline with model {self.model_id}...")
        
        env = os.environ.copy()
        # Remove venv vars so child uv processes resolve their own project-local venvs
        for key in ["VIRTUAL_ENV", "CONDA_PREFIX", "CONDA_DEFAULT_ENV"]:
            env.pop(key, None)
        if self.model_id:
            env["ROUTER_MODEL_ID"] = self.model_id
        if self.adapter_path:
            env["ROUTER_ADAPTER_PATH"] = self.adapter_path
            
        if self.pipeline == "lightning":
            cwd = os.path.join(self.base_dir, "LightningRoute")
            venv_bin = os.path.join(cwd, ".venv", "bin")
            cmd = [os.path.join(venv_bin, "lightning-route"), "serve",
                   "--model", self.model_id, "--port", "8000"]
            if self.adapter_path:
                cmd.extend(["--adapter", self.adapter_path])
            self._launch(cmd, cwd, env, "lightning")
            self._wait_for_health("http://127.0.0.1:8000/docs", timeout=300)
            
        elif self.pipeline == "llm":
            cwd = os.path.join(self.base_dir, "LLM-based_router")
            venv_bin = os.path.join(cwd, ".venv", "bin")
            env["PYTHONPATH"] = os.path.join(cwd, "src")
            cmd = [os.path.join(venv_bin, "uvicorn"),
                   "llm_router.server:app", "--port", "8000"]
            self._launch(cmd, cwd, env, "llm")
            self._wait_for_health("http://127.0.0.1:8000/docs", timeout=300)
            
        elif self.pipeline == "rizzo":
            rizzo_dir = "/Users/francescodedominicis/Desktop/THESIS/Jevlike_repos/rizzo-flow"
            venv_bin = os.path.join(rizzo_dir, ".venv", "bin")
            print("⏳ Waiting for native Rizzo-Flow to boot on port 8017 (this may take a while)...")
            self._launch([os.path.join(venv_bin, "rizzo"), "serve"], rizzo_dir, env, "rizzo")
            self._wait_for_health("http://127.0.0.1:8017/docs", timeout=300)

    def _launch(self, cmd, cwd, env, name):
        log_path = os.path.join(LOG_DIR, f"{name}.log")
        log_file = open(log_path, "w")
        self.log_files.append(log_file)
        print(f"   📄 Server logs -> {log_path}")
        print(f"   🔧 Command: {' '.join(cmd)}")
        print(f"   📂 CWD: {cwd}")
        p = subprocess.Popen(
            cmd,
            cwd=cwd, env=env,
            stdout=log_file, stderr=subprocess.STDOUT
        )
        self.processes.append(p)
        # Give it a moment to crash immediately if something is wrong
        time.sleep(2)
        ret = p.poll()
        if ret is not None:
            log_file.flush()
            with open(log_path, "r") as f:
                output = f.read()
            raise RuntimeError(
                f"Server process exited immediately with code {ret}.\n"
                f"--- Server Log ({log_path}) ---\n{output}"
            )
            
    def _wait_for_health(self, url: str, timeout: int = 300):
        start = time.time()
        while time.time() - start < timeout:
            # Check if the process died
            for p in self.processes:
                ret = p.poll()
                if ret is not None:
                    # Process died, dump logs
                    self._dump_logs()
                    raise RuntimeError(f"Server process died with exit code {ret}. Check logs above.")
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    time.sleep(2)
                    print(f"✅ Server at {url} is up!")
                    return
            except (requests.ConnectionError, requests.Timeout):
                pass
            time.sleep(2)
        self._dump_logs()
        raise TimeoutError(f"Server at {url} failed to boot within {timeout} seconds. Check logs above.")
    
    def _dump_logs(self):
        """Print the last 50 lines of each server log for debugging."""
        for lf in self.log_files:
            lf.flush()
            path = lf.name
            print(f"\n--- Server Log ({path}) ---")
            try:
                with open(path, "r") as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        print(f"  {line}", end="")
            except Exception as e:
                print(f"  (Could not read log: {e})")
            print("--- End of Log ---\n")
        
    def stop(self):
        print(f"🛑 Shutting down {self.pipeline} pipeline...")
        for p in self.processes:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        self.processes = []
        for lf in self.log_files:
            try:
                lf.close()
            except Exception:
                pass
        self.log_files = []
        time.sleep(3)

