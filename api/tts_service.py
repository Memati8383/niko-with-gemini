import os
import asyncio
import tempfile
import base64
import logging
import sys

logger = logging.getLogger("NikoAI.TTS")

class TTSService:
    def __init__(self):
        self.applio_dir = os.path.abspath("Applio")
        self.applio_python = os.path.join(self.applio_dir, "env", "python.exe")
        self.core_py = os.path.join(self.applio_dir, "core.py")
        
        # User model paths
        self.pth_path = os.path.join(self.applio_dir, "logs", "my-project", "my-project_200e_5200s.pth")
        self.index_path = os.path.join(self.applio_dir, "logs", "my-project", "my-project.index")
        
        # Determine the backend python executable to run edge-tts
        self.main_python = sys.executable
        
    async def generate_rvc_audio(self, text: str, voice: str = "tr-TR-AhmetNeural") -> str:
        """
        Generates TTS audio from text and converts it using the user's RVC model.
        Returns the final audio as base64 encoded string.
        """
        if not text.strip():
            return ""
            
        temp_tts_fd, temp_tts_path = tempfile.mkstemp(suffix=".wav")
        temp_rvc_fd, temp_rvc_path = tempfile.mkstemp(suffix=".wav")
        os.close(temp_tts_fd)
        os.close(temp_rvc_fd)
        
        try:
            # 1. Run edge-tts
            logger.info("Generating edge-tts audio...")
            edge_cmd = [
                self.main_python, "-m", "edge_tts",
                "--text", text,
                "--voice", voice,
                "--write-media", temp_tts_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *edge_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"edge-tts failed: {stderr.decode('utf-8', errors='ignore')}")
                return ""
                
            # 2. Run Applio RVC infer
            logger.info("Applying RVC model...")
            rvc_cmd = [
                self.applio_python, self.core_py, "infer",
                "--input_path", temp_tts_path,
                "--output_path", temp_rvc_path,
                "--pth_path", self.pth_path,
                "--index_path", self.index_path,
                "--f0_method", "rmvpe",
                "--protect", "0.33",
                "--index_rate", "0.3"
            ]
            
            process_rvc = await asyncio.create_subprocess_exec(
                *rvc_cmd,
                cwd=self.applio_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_rvc, stderr_rvc = await process_rvc.communicate()
            
            if process_rvc.returncode != 0:
                logger.error(f"RVC infer failed: {stderr_rvc.decode('utf-8', errors='ignore')}")
                # Fallback: if RVC fails, return the original edge-tts audio so the user still hears something
                temp_rvc_path = temp_tts_path
            
            # 3. Read and base64 encode
            with open(temp_rvc_path, "rb") as f:
                audio_data = f.read()
                
            return base64.b64encode(audio_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error in generate_rvc_audio: {e}")
            return ""
        finally:
            # Clean up
            try:
                if os.path.exists(temp_tts_path):
                    os.remove(temp_tts_path)
                # Note: if RVC failed and we used temp_tts_path as temp_rvc_path, we shouldn't try to delete temp_tts_path again if it's already deleted
                if temp_rvc_path != temp_tts_path and os.path.exists(temp_rvc_path):
                    os.remove(temp_rvc_path)
            except Exception as e:
                logger.error(f"Error cleaning up temp files: {e}")

# Create a singleton instance
tts_service = TTSService()
