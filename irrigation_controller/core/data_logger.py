import json
import os


class DataLogger:
    def __init__(self, sd_driver, mount_point="/sd"):
        self.sd = sd_driver
        self.mount_point = mount_point
        self.is_mounted = False
        self._mount()

    def _mount(self):
        try:
            # Check if already mounted
            try:
                os.listdir(self.mount_point)
                self.is_mounted = True
                print(f"[SD] Ya montada en {self.mount_point}")
                return
            except Exception:
                pass

            # Mount
            vfs = os.VfsFat(self.sd)
            os.mount(vfs, self.mount_point)
            self.is_mounted = True
            print(f"[SD] Montada exitosamente en {self.mount_point}")
        except Exception as e:
            print(f"[SD] Error montando SD: {e}")
            self.is_mounted = False

    def save_data(self, data, filename):
        if not self.is_mounted:
            print("[SD] No montada. Reintentando montaje...")
            self._mount()
            if not self.is_mounted:
                return False

        filepath = f"{self.mount_point}/{filename}"
        try:
            with open(filepath, "a") as f:
                json.dump(data, f)
                f.write("\n")
            # Sync to ensure physical write
            os.sync()
            print(f"[SD] Datos guardados en {filepath}")
            return True
        except Exception as e:
            print(f"[SD] Error escribiendo en {filepath}: {e}")
            return False
