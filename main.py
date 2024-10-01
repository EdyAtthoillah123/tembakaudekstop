import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
import time
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
import serial
import time
import matplotlib.image as mpimg

class WebcamApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Webcam App")

        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)  # Ensure the camera index is correct
        if not self.video_capture.isOpened():
            print("Error: Could not open video capture.")
            return

        self.current_image = None

        # Styling configuration
        self.window.configure(bg="#2c3e50")
        self.window.geometry("960x600")

        # Grid configuration for responsiveness
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        # Webcam display with border and shadow effect
        self.frame_webcam = tk.Frame(window, bg="#2c3e50", bd=2, relief=tk.RAISED)
        self.frame_webcam.grid(row=0, column=0, padx=20, pady=20)

        self.canvas_webcam = tk.Canvas(
            self.frame_webcam, width=640, height=480, bg="#34495e", bd=0, highlightthickness=0
        )
        self.canvas_webcam.pack()

        # Modern label with rounded corners
        self.label_frame = tk.Frame(window, bg="#34495e", bd=5, relief=tk.FLAT)
        self.label_frame.grid(row=0, column=1, sticky=tk.NW, padx=20, pady=20)

        self.label_dimensions = tk.Label(
            self.label_frame, text="", font=("Arial", 14, "bold"), fg="#ecf0f1", bg="#34495e", padx=10, pady=10
        )
        self.label_dimensions.pack(anchor=tk.NW)

        # Capture Button with modern style and icon
        self.button_capture = tk.Button(
            window, text="Mulai", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c",
            activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
            command=self.download_image
        )
        self.button_capture.grid(row=1, column=0, pady=20, padx=20)

        # Close Button with hover effect
        self.button_close = tk.Button(
            window, text="Close", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c",
            activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
            command=self.on_closing
        )
        self.button_close.grid(row=1, column=1, pady=20, padx=20)

        self.button_close.bind("<Enter>", self.on_enter)
        self.button_close.bind("<Leave>", self.on_leave)

        # Start video loop
        self.update_frame()

        # Aktifkan auto capture dengan interval 100 milidetik
        self.capture_interval = 1000 # Set capture interval to 100 milliseconds
        self.auto_capture()  # Start auto capture

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas_webcam.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(10, self.update_frame)

    def auto_capture(self):
        self.download_image()
        self.window.after(self.capture_interval, self.auto_capture)

    def on_closing(self):
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.window.quit()

    def on_enter(self, e):
        e.widget['bg'] = '#d35400'

    def on_leave(self, e):
        e.widget['bg'] = '#e74c3c'

    def download_image(self):
        if self.current_image is not None:
            directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
            if not os.path.exists(directory):
                os.makedirs(directory)
            # Save the image with a unique name using the current timestamp
            file_path = os.path.join(directory, f"captured_image_{int(time.time())}.jpg")
            try:
                self.current_image.save(file_path)
                # Process the saved image
                self.process_image(file_path)
            except PermissionError as e:
                print(f"Permission denied: {e}")
        else:
            print("No image to save!")


    def process_image(self, path):
        if os.path.exists(path):
            # Membaca gambar dari path yang diberikan
            image = mpimg.imread(path)

            if image is None:
                print("Gambar tidak ditemukan di path:", path)
                return
                 # Konversi gambar ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

            # Segmentasi Citra Menggunakan Thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)

            # Temukan Kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Deteksi kerusakan dan minyak 
                cropped_image = image[y:y+h, x:x+w]

                # Buat masker untuk citra yang dipotong
                mask = np.zeros((h, w), dtype=np.uint8)

                # Sesuaikan koordinat kontur ke citra yang dipotong
                adjusted_contour = largest_contour - [x, y]

                # Isi area kontur pada masker
                cv2.drawContours(mask, [adjusted_contour], -1, 255, thickness=cv2.FILLED)

                # Segmentasikan objek dengan masker
                segmented_image = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
                cv2.imwrite('segmentedd.png', segmented_image)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)
                    
                    # Simpan citra grayscale hasil segmentasi ke file dengan nama dan ekstensi yang benar
                    cv2.imwrite('segmented_image_gray.png', segmented_image_gray)

                    # Menggunakan blur untuk menghilangkan noise
                    blurred = cv2.GaussianBlur(segmented_image_gray, (3, 5), 0)

                    cv2.imwrite('gaussian.png', blurred)

                    # Deteksi tepi menggunakan algoritma Canny
                    edges = cv2.Canny(blurred, 50, 10)
                    
                    cv2.imwrite('edges.png', edges)

                    # Temukan kontur di gambar hasil deteksi tepi
                    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    # Tentukan rentang warna putih
                    lower_white = np.array([130], dtype=np.uint8)
                    upper_white = np.array([255], dtype=np.uint8)
                    
                    # Buat mask untuk warna putih
                    white_mask = cv2.inRange(segmented_image_gray, lower_white, upper_white)
                    white_pixels = cv2.countNonZero(white_mask)

                    # Cari kontur di white_mask
                    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    # Ganti piksel putih dengan warna kuning pada gambar BGR
                    white_mask_bgr = cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)
                    white_mask_bgr[np.where((white_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

                    # Inisialisasi jumlah bounding box
                    jumlah_bounding_box = 0

                        # Gambar bounding box di sekitar kontur (lubang) dan hitung ukuran dalam cm
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)

                        # Hitung ukuran dalam cm (dengan asumsi 1 pixel = 1 cm)
                        lebar_cm = w * 0.075  # Lebar bounding box dalam cm
                        tinggi_cm = h * 0.081 # Tinggi bounding box dalam cm

                        # Cek jika lebar atau tinggi lebih dari threshold (misal 0.5 cm)
                        if lebar_cm > 0.2 and tinggi_cm > 0.2:
                            # Gambar bounding box jika ukuran lebih dari 0.5 cm
                            cv2.rectangle(white_mask_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            # Tampilkan ukuran bounding box di atas dan samping bounding box
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.5
                            font_color = (255, 255, 255)  # Warna putih
                            thickness = 1

                            # Tampilkan lebar di atas bounding box
                            text_lebar = f'L: {lebar_cm:.2f} cm'
                            cv2.putText(white_mask_bgr, text_lebar, (x, y - 10), font, font_scale, font_color, thickness)

                            # Tampilkan tinggi di samping bounding box
                            text_tinggi = f'T: {tinggi_cm:.2f} cm'
                            cv2.putText(white_mask_bgr, text_tinggi, (x + w + 10, y + h // 2), font, font_scale, font_color, thickness)

                            print(f'Bounding Box {jumlah_bounding_box + 1}: Lebar = {lebar_cm:.2f} cm, Tinggi = {tinggi_cm:.2f} cm')

                            # Tambahkan jumlah bounding box
                            jumlah_bounding_box += 1
                        else:
                            print(f'Kontur diabaikan: Lebar = {lebar_cm:.2f} cm, Tinggi = {tinggi_cm:.2f} cm (di bawah threshold 0.5 cm)')

                    # Simpan hasil gambar dengan bounding box
                    cv2.imwrite('whiteMaskBgr.png', white_mask_bgr)

                    # Hitung total piksel putih
                    white_pixels = cv2.countNonZero(white_mask)
                    print(f'Jumlah piksel putih di dalam daun: {white_pixels}')
                    print(f'Jumlah bounding box (lubang): {jumlah_bounding_box}')


                    if jumlah_bounding_box >= 1:
                        Kerusakan = "Rambing"
                    else:
                        Kerusakan = "Utuh"

                    # Ubah gambar grayscale menjadi BGR
                    segmented_image_bgr = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)

                    # Gabungkan gambar BGR dengan mask kuning dan bounding box hijau
                    combined_image = cv2.addWeighted(segmented_image_bgr, 0.7, white_mask_bgr, 0.3, 0)

                    # Simpan gambar hasil gabungan
                    cv2.imwrite('combined_output.png', combined_image)
                              # Update label with processed information
                    self.label_dimensions.config(
                        # \nWarna  :  {dominant_value}\nFrekwensi :  {dominant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                        text=f"Kerusakan: {Kerusakan}"
                    )

                else:
                    print("Segmented Not Found")
            else:
                print("Contour Not Found")
        else:
            print("Image path not found.")

    def determine_leaf_quality(self, panjang):
        if panjang < 5:
            return "-"
        elif panjang > 45:
            return "Super"
        elif 40 <= panjang <= 45:
            return "Lente 1"
        elif 35 <= panjang < 40:
            return "Lente 2"
        elif 30 <= panjang < 35:
            return "Lente 3"
        else:
            return "Filler"

root = tk.Tk()
app = WebcamApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
