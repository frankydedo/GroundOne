# pyrefly: ignore [missing-import]
import whisper
import warnings

# Suppress FP16 warnings on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def main():
    print("Loading Whisper model (large) on CPU (natively on Apple Silicon)...")
    model = whisper.load_model("large")
    
    print("Starting transcription of jev_simone_rizzo.mp3 with anti-hallucination settings...")
    result = model.transcribe(
        "jev_simone_rizzo.mp3",
        language="it",
        condition_on_previous_text=False,
        initial_prompt="Questa è una trascrizione accurata di un video YouTube di tecnologia su AI, modelli GEV, e System One Models, spiegato in modo colloquiale in italiano."
    )
    
    print("Transcription complete. Saving to jev_simone_rizzo.txt...")
    with open("jev_simone_rizzo.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
        
    print("Done!")

if __name__ == "__main__":
    main()
