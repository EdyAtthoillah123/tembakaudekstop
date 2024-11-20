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
import matplotlib.pyplot as plt

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
            image = mpimg.imread(path)
            originalImage = cv2.imread(path)

            if image is None:
                print("Gambar tidak ditemukan di path:", path)
                return
            # Meningkatkan kontras dan kecerahan
            alpha = 4  # Faktor kontras (1.0 = tidak ada perubahan)
            beta = 0    # Faktor kecerahan (positif = lebih terang, negatif = lebih gelap)
            enhancedImage = cv2.convertScaleAbs(originalImage, alpha=alpha, beta=beta)

            # Menyimpan hasil gambar
            cv2.imwrite("Original_Image.png", originalImage)
            cv2.imwrite("Enhanced_Image.png", enhancedImage)
            print("Gambar asli dan gambar dengan kontras tinggi berhasil disimpan.")
                    # Konversi gambar ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

            # Segmentasi Citra Menggunakan Thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)

            # Temukan Kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                pixel_panjang = w
                pixel_lebar = h
                # Hitung dimensi
                panjang = 0.0895 * pixel_panjang - 3.1795

                # Deteksi kerusakan dan minyak 
                cropped_image = enhancedImage[y:y+h, x:x+w]

                # Buat masker untuk citra yang dipotong
                mask = np.zeros((h, w), dtype=np.uint8)

                # Sesuaikan koordinat kontur ke citra yang dipotong
                adjusted_contour = largest_contour - [x, y]

                # Isi area kontur pada masker
                cv2.drawContours(mask, [adjusted_contour], -1, 255, thickness=cv2.FILLED)

                # Segmentasikan objek dengan masker
                segmented_image = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
                cv2.imwrite('segmentedd.png', segmented_image)
                # Temukan kontur pada gambar masker
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Buat gambar kosong dengan ukuran yang sama dengan segmented_image
                inner_mask = np.zeros_like(mask)

                # Loop melalui setiap kontur yang ditemukan
                for contour in contours:
                    # Shrink kontur ke dalam dengan jarak 30 piksel menggunakan offset
                    offset_distance = 25

                    # Buat offset dengan -30 piksel ke dalam menggunakan `cv2.drawContours`
                    # Offset dilakukan dengan menggeser titik-titik kontur ke dalam menggunakan erosi
                    eroded_mask = np.zeros_like(mask)
                    cv2.drawContours(eroded_mask, [contour], -1, 255, thickness=cv2.FILLED)
                    
                    # Menggunakan erosi untuk membuat kontur baru di dalam kontur asli
                    kernel = np.ones((offset_distance, offset_distance), np.uint8)
                    inner_contour_mask = cv2.erode(eroded_mask, kernel, iterations=1)

                    # Temukan kontur baru pada inner_contour_mask
                    inner_contours, _ = cv2.findContours(inner_contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    # Gambar kontur baru ke inner_mask
                    cv2.drawContours(inner_mask, inner_contours, -1, 255, thickness=cv2.FILLED)

                # Terapkan inner_mask sebagai masker ke gambar asli yang di-cropped
                result_with_inner_contour = cv2.bitwise_and(cropped_image, cropped_image, mask=inner_mask)

                # Simpan hasil akhir dengan kontur di dalam kontur
                cv2.imwrite('result_with_inner_contour.png', result_with_inner_contour)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('6_segmented_image_gray.png', segmented_image_gray)
                    
                    inner_segmented_gray = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('Inner_Segmented_Gray.png', inner_segmented_gray)
                                        # Tentukan rentang warna putih
                    lower_white = np.array([173], dtype=np.uint8)
                    upper_white = np.array([180], dtype=np.uint8)
                    
                    # Buat mask untuk warna putih
                    white_mask = cv2.inRange(inner_segmented_gray, lower_white, upper_white)
                    white_pixels = cv2.countNonZero(white_mask)
                    
                    # Hitung total piksel pada gambar
                    total_pixels = inner_segmented_gray.shape[0] * inner_segmented_gray.shape[1]
                    
                    # Hitung presentase piksel putih
                    white_percentage = (white_pixels / total_pixels) * 100
                    
                    # Ganti piksel putih dengan warna kuning pada gambar BGR
                    white_mask_bgr = cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)
                    white_mask_bgr[np.where((white_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]
                    cv2.imwrite('WhiteMaskBgr.png', white_mask_bgr)
                    
                    print(f"Jumlah piksel putih: {white_pixels}")
                    print(f"Total piksel: {total_pixels}")
                    print(f"Presentase piksel putih: {white_percentage:.2f}%")

                    if white_percentage >= 4:
                        UniformCategory = "Tajem"
                    else:
                        UniformCategory = "Laen"

                    inner_segmented_hsv= cv2.cvtColor(result_with_inner_contour, cv2.COLOR_BGR2HSV)
                  
                    segmented_image_hsv = cv2.cvtColor(inner_segmented_hsv, cv2.COLOR_BGR2HSV)
                    cv2.imwrite('Image_Inner_HSV.png', segmented_image_hsv)
                    
                    # Rentang bawah dan atas warna kuning# Rentang bawah dan atas warna kuning
                    lower_yellow = np.array([20, 100, 100])  # H, S, V
                    upper_yellow = np.array([40, 255, 255])  # H, S, V

                    # Buat masker untuk mendeteksi warna kuning
                    yellow_mask = cv2.inRange(segmented_image_hsv, lower_yellow, upper_yellow)

                    # Hitung jumlah piksel warna kuning (255 dalam mask)
                    yellow_pixels = cv2.countNonZero(yellow_mask)

                    # Hitung total piksel dalam gambar
                    total_pixels = image.shape[0] * image.shape[1]

                    # Hitung persentase warna kuning
                    percentage_yellow = (yellow_pixels / total_pixels) * 100

                    # Print hasil
                    print(f"Jumlah piksel kuning yang diblokir: {yellow_pixels}")
                    print(f"Persentase warna kuning di gambar: {percentage_yellow:.2f}%")

                    # Blokir warna kuning dengan mengganti pikselnya menjadi hitam
                    # Asumsikan 'result_with_inner_contour' adalah gambar asli
                    blocked_image = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=~yellow_mask)

                    # Simpan gambar hasil pemblokiran warna kuning
                    cv2.imwrite('blockingHSV.png', blocked_image)

                    # Pisahkan channel H, S, V
                    hue_channel = inner_segmented_hsv[:, :, 0]
                    saturation_channel = inner_segmented_hsv[:, :, 1]
                    value_channel = inner_segmented_hsv[:, :, 2]            

                    # Hitung statistik untuk Hue
                    hue_mean = np.mean(hue_channel)
                    hue_std_dev = np.std(hue_channel)
                    hue_variance = np.var(hue_channel)

                    # Hitung statistik untuk Saturation
                    saturation_mean = np.mean(saturation_channel)
                    saturation_std_dev = np.std(saturation_channel)
                    saturation_variance = np.var(saturation_channel)

                    # Hitung statistik untuk Value
                    value_mean = np.mean(value_channel)
                    value_std_dev = np.std(value_channel)
                    value_variance = np.var(value_channel)

                    # if 7.7 < hue_mean < 9 and 108 <= saturation_mean <= 130 and 77 <= value_mean <= 100:
                    #     UniformCategory = "Tajem"
                    # else:
                    #     UniformCategory = "Laen"


                    self.label_dimensions.config(
                        # \nWarna  :  {dominant_value}\nFrekwensi :  {domi`nant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                        text=f"Grade: {UniformCategory}\nrata2 Hue: {hue_mean:.1f}\nrata2 Saturasi: {saturation_mean:.1f}\nrata2 Value: {value_mean:.1f}"
                    )
              
                else: 
                    print("Segmented Not Found")
            else:
                print("Contour Not Found")
        else:
            print("Image path not found.")

    def send_hue_and_color_category(self, hue_value, color_category):
        data = f"{hue_value},{color_category}\n"
        self.arduino.write(data.encode())  # Kirim data ke Arduino
        print(f"Data dikirim: {data.strip()}")

root = tk.Tk()
app = WebcamApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()