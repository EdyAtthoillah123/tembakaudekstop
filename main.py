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
        self.window.title("TARO")

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
            cv2.imwrite('1_originalImage.png', image)

            if image is None:
                print("Gambar tidak ditemukan di path:", path)
                return

            # Proses 1: Konversi gambar ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            cv2.imwrite('2_grayscaleImage.png', img_gray)

            # Proses 2: Segmentasi Citra Menggunakan Thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
            cv2.imwrite('3_thresholdImage.png', thresh)

            # Temukan Kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Proses 3: Potong gambar sesuai bounding box kontur terbesar
                cropped_image = image[y:y+h, x:x+w]
                cv2.imwrite('4_croppedImage.png', cropped_image)

                # Buat masker untuk citra yang dipotong
                mask = np.zeros((h, w), dtype=np.uint8)

                # Sesuaikan koordinat kontur ke citra yang dipotong
                adjusted_contour = largest_contour - [x, y]

                # Isi area kontur pada masker
                cv2.drawContours(mask, [adjusted_contour], -1, 255, thickness=cv2.FILLED)

                # Segmentasikan objek dengan masker
                segmented_image = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
                cv2.imwrite('5_segmentedImage.png', segmented_image)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('6_segmented_image_gray.png', segmented_image_gray)

                    if contours:
                        largest_contour = max(contours, key=cv2.contourArea)
                        
                        # Menghitung perimeter, area, dan compactness hanya jika ada kontur
                        perimeter = cv2.arcLength(largest_contour, True)  # Panjang perimeter kontur
                        area = cv2.contourArea(largest_contour)  # Luas area kontur
                        compactness = (perimeter ** 2) / (4 * np.pi * area)  # Menghitung compactness (rasio keliling & area)

                        # Gambar kontur pada gambar asli (atau gambar grayscale)
                        image_with_contours = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)  # Pastikan gambar menjadi 3 channel untuk warna
                        cv2.drawContours(image_with_contours, [largest_contour], -1, (0, 255, 0), 2)  # Gambar kontur pada gambar

                        # Tambahkan teks informasi perimeter, area, dan compactness
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.5
                        font_color = (255, 255, 255)  # Putih
                        thickness = 1

                        # Tampilkan perimeter, area, dan compactness di gambar
                        text_perimeter = f'Perimeter: {perimeter:.2f}'
                        text_area = f'Area: {area:.2f}'
                        text_compactness = f'Compactness: {compactness:.2f}'

                        cv2.putText(image_with_contours, text_perimeter, (10, 30), font, font_scale, font_color, thickness)
                        cv2.putText(image_with_contours, text_area, (10, 50), font, font_scale, font_color, thickness)
                        cv2.putText(image_with_contours, text_compactness, (10, 70), font, font_scale, font_color, thickness)

                        # Simpan gambar dengan informasi tepi dan kekasaran
                        cv2.imwrite('output_edge_detection_with_info.png', image_with_contours)

                    else:
                        print("Tidak ditemukan kontur pada gambar.")

                    # Simpan gambar yang menunjukkan hasil deteksi tepi daun
                    result_contour_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                    cv2.drawContours(result_contour_image, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.imwrite('7_contour_detection_result.png', result_contour_image)

                    # Proses 5: Tentukan rentang warna putih untuk deteksi area dalam daun
                    lower_white = np.array([150], dtype=np.uint8)
                    upper_white = np.array([255], dtype=np.uint8)
                    white_mask = cv2.inRange(segmented_image_gray, lower_white, upper_white)
                    white_pixels = cv2.countNonZero(white_mask)

                    # Cari kontur di white_mask
                    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    white_mask_bgr = cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)
                    white_mask_bgr[np.where((white_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

                    jumlah_bounding_box = 0
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)

                        # Hitung ukuran dalam cm
                        lebar_cm = w * 0.075
                                                                                                                                                                                                                                                                                                                                                                                                                    
                        tinggi_cm = h * 0.081

                        if lebar_cm > 0.2 and tinggi_cm > 0.2:
                            cv2.rectangle(white_mask_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.5
                            font_color = (255, 255, 255)
                            thickness = 1

                            text_lebar = f'L: {lebar_cm:.2f} cm'
                            cv2.putText(white_mask_bgr, text_lebar, (x, y - 10), font, font_scale, font_color, thickness)

                            text_tinggi = f'T: {tinggi_cm:.2f} cm'
                            cv2.putText(white_mask_bgr, text_tinggi, (x + w + 10, y + h // 2), font, font_scale, font_color, thickness)

                            print(f'Bounding Box {jumlah_bounding_box + 1}: Lebar = {lebar_cm:.2f} cm, Tinggi = {tinggi_cm:.2f} cm')
                            jumlah_bounding_box += 1
                        else:
                            print(f'Kontur diabaikan: Lebar = {lebar_cm:.2f} cm, Tinggi = {tinggi_cm:.2f} cm (di bawah threshold 0.5 cm)')

                    # Simpan gambar hasil deteksi lubang pada daun
                    cv2.imwrite('8_whiteMaskBgr.png', white_mask_bgr)

                    # Ambang batas kekasaran
                    threshold_rusak = 1.8  # Nilai compactness > 1.2 dapat dianggap rusak
                    print("Compacness: ", compactness)
                    print("Thickness: ", threshold_rusak)

                    if jumlah_bounding_box >= 1 and compactness <= threshold_rusak:
                        Kerusakan = "Rambing Bolong"
                    elif compactness > threshold_rusak and jumlah_bounding_box == 0:
                        print("Deteksi: Tepi Daun Rusak")
                        Kerusakan = "Tepi Daun Rusak"
                    elif compactness > threshold_rusak and jumlah_bounding_box >= 1:
                        Kerusakan = "Bolong dan Tepi Rusak"
                    elif jumlah_bounding_box == 0 and compactness <= threshold_rusak:
                        Kerusakan = "Utuh"
                    else:
                        print("Deteksi: Tepi Daun Sempurna")
                        Kerusakan = "Utuh"
                    

                    # Hitung jumlah piksel putih dan jumlah bounding box
                    white_pixels = cv2.countNonZero(white_mask)
                    print(f'Jumlah piksel putih di dalam daun: {white_pixels}')
                    print(f'Jumlah bounding box (lubang): {jumlah_bounding_box}')

                    # Gabungkan gambar BGR dengan mask kuning dan bounding box hijau
                    segmented_image_bgr = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)
                    combined_image = cv2.addWeighted(segmented_image_bgr, 0.7, white_mask_bgr, 0.3, 0)

                    # Simpan gambar hasil gabungan dari deteksi kontur dan lubang
                    cv2.imwrite('9_combined_output.png', combined_image)

                    # Update label untuk menampilkan hasil kerusakan
                    self.label_dimensions.config(text=f"Kerusakan: \n{Kerusakan}")
                else:
                    print("Segmented Image Not Found")
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
