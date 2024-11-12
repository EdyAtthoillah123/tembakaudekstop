import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
import serial
import time
import matplotlib.image as mpimg
import serial
import time
import mahotas
import os
from skimage.feature import graycomatrix, graycoprops

try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Tunggu beberapa detik agar koneksi stabil
    print("Koneksi berhasil ke Arduino!")
    arduino.close()  # Tutup koneksi setelah pengujian
except serial.SerialException as e:
    print(f"Kesalahan: {e}")

class WebcamApp:
    def __init__(self, window):
        self.arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)  # Tunggu agar koneksi serial stabil
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
        self.capture_interval = 500 # Set capture interval to 100 milliseconds
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
            image = cv2.imread(path)

            if image is None:
                print("Image not found at path:", path)
                return

            # Simpan gambar asli
            cv2.imwrite("Original_Image.png", image)
            print("Image successfully read and saved as 'Original_Image.png'.")

            # Konversi gambar ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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
                adjusted_contour = largest_contour - [x, y]
                cv2.drawContours(mask, [adjusted_contour], -1, 255, thickness=cv2.FILLED)
                segmented_image = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
                cv2.imwrite('2_Image_Segmented.png', segmented_image)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite('4_segmented_image_gray.png', segmented_image_gray)

                    # Perhitungan GLCM
                    glcm = graycomatrix(segmented_image_gray, distances=[1], angles=[0], symmetric=True, normed=True)

                    # Normalisasi dan konversi GLCM ke format yang bisa disimpan sebagai gambar
                    glcm_image = (glcm[:, :, 0, 0] * 255).astype(np.uint8)
                    cv2.imwrite("GLCM_Matrix.png", glcm_image)
                    print("GLCM matrix saved as 'GLCM_Matrix.png'.")

                    # Ekstraksi fitur GLCM
                    contrast = graycoprops(glcm, 'contrast')[0, 0]
                    dissimilarity = graycoprops(glcm, 'dissimilarity')[0, 0]
                    homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
                    energy = graycoprops(glcm, 'energy')[0, 0]
                    correlation = graycoprops(glcm, 'correlation')[0, 0]

                        # Menentukan kategori tekstur berdasarkan threshold
                    if contrast <= 115:
                        texture = "Halus"
                    elif 115 < contrast <= 120:
                        texture = "Sedang"
                    else:
                        texture = "Kasar"

                    # Cetak hasil GLCM
                    print("GLCM Features:")
                    print(f"Contrast: {contrast}")
                    print(f"Dissimilarity: {dissimilarity}")
                    print(f"Homogeneity: {homogeneity}")
                    print(f"Energy: {energy}")
                    print(f"Correlation: {correlation}")
                    self.label_dimensions.config(
                        text=f"Texture: {texture}\ncontrast: {contrast:.3f}\nDissimilarity: {dissimilarity:.3f}\nHomogenity: {homogeneity:.3f}\nEnergy: {energy:.3f}\nCorrelation: {correlation:.3f}"
                    )

                else:
                    print("Segmented Not Found")
            else:
                print("Contour Not Found")
        else:
            print("Image path not found.")

root = tk.Tk()
app = WebcamApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()