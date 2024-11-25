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
            alphaMedium = 3  # Faktor kontras (1.0 = tidak ada perubahan)
            betaMEdium = 0    # Faktor kecerahan (positif = lebih terang, negatif = lebih gelap)
            enhancedImageMedium = cv2.convertScaleAbs(originalImage, alpha=alphaMedium, beta=betaMEdium)

            # Menyimpan hasil gambar
            cv2.imwrite("1_Original_Image.png", originalImage)
            cv2.imwrite("2_Enhanced_Image.png", enhancedImage)
            cv2.imwrite("2_Enhanced_Image_Medium.png", enhancedImageMedium)
            print("Gambar asli dan gambar dengan kontras tinggi berhasil disimpan.")


            cv2.imwrite("Original_Image.png", image)
            # Konversi gambar dari BGR ke HSV
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Tentukan ukuran area untuk ekstraksi nilai (50x50)
            area_size = 175

            # Tentukan posisi untuk mengambil area 50x50 (misalnya di pusat gambar)
            height, width, _ = hsv_image.shape
            start_x = (width // 2) - (area_size // 2)
            start_y = (height // 2) - (area_size // 2)

            # Ekstraksi area 50x50
            hsv_area = hsv_image[start_y:start_y + area_size, start_x:start_x + area_size]

            # Pisahkan channel Hue, Saturation, dan Value
            hue_channel = hsv_area[:, :, 0]  # Channel Hue
            saturation_channel = hsv_area[:, :, 1]  # Channel Saturation
            value_channel = hsv_area[:, :, 2]  # Channel Value

            # Hitung jumlah total data Hue, Saturation, dan Value dalam area 50x50
            sum_hue = np.sum(hue_channel)
            sum_saturation = np.sum(saturation_channel)
            sum_value = np.sum(value_channel)

            # Menghitung rata-rata nilai Hue, Saturation, dan Value
            average_hue = sum_hue / (area_size * area_size)  # Karena area 50x50, jumlah total piksel adalah 2500
            average_saturation = sum_saturation / (area_size * area_size)
            average_value = sum_value / (area_size * area_size)

            # Menyimpan area 50x50 dan gambar HSV
            cv2.imwrite("hsv_area_50x50.png", hsv_area)

            # Debug print statements x 
            print(f"Average Hue: {average_hue}")
            print(f"Average Saturation: {average_saturation}")
            print(f"Average Value: {average_value}")


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
                cv2.imwrite('3_segmentedd.png', segmented_image)
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
                cv2.imwrite('4_result_with_inner_contour.png', result_with_inner_contour)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('5_segmented_image_gray.png', segmented_image_gray)
                    
                    inner_segmented_gray = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('6_Inner_Segmented_Gray.png', inner_segmented_gray)
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
                    cv2.imwrite('7_WhiteMaskBgr.png', white_mask_bgr)
                    
                    print(f"Jumlah piksel putih: {white_pixels}")
                    print(f"Total piksel: {total_pixels}")
                    print(f"Presentase piksel putih: {white_percentage:.2f}%")

                    if white_percentage >= 4:
                        UniformCategory = "Tajem"
                    else:
                        UniformCategory = "Laen"

                    inner_segmented_hsv= cv2.cvtColor(result_with_inner_contour, cv2.COLOR_BGR2HSV)
                  
                    segmented_image_hsv = cv2.cvtColor(inner_segmented_hsv, cv2.COLOR_BGR2HSV)
                    cv2.imwrite('8_Image_Inner_HSV.png', segmented_image_hsv)
                    
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
                    cv2.imwrite('9_blockingHSV.png', blocked_image)

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
                    inner_segmented_hsv = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_BGR2HSV)

                    # Definisikan rentang untuk berbagai tingkatan kuning
                    lower_light_yellow = np.array([20, 50, 150])  # Kuning pucat
                    upper_light_yellow = np.array([30, 150, 255])

                    lower_medium_yellow = np.array([20, 200, 100])  # Kuning medium
                    upper_medium_yellow = np.array([25, 250, 255])

                    lower_bright_yellow = np.array([30, 200, 200])  # Kuning terang
                    upper_bright_yellow = np.array([40, 255, 255])

                    lower_brightest_yellow = np.array([30, 225, 225])  # Kuning terang
                    upper_brightest_yellow = np.array([40, 255, 255])

                    lower_brightFinal_yellow = np.array([20, 225, 225])  # Kuning terang
                    upper_brightFinal_yellow = np.array([25, 255, 255])

                    # Mask untuk setiap gradien
                    mask_light_yellow = cv2.inRange(inner_segmented_hsv, lower_light_yellow, upper_light_yellow)
                    mask_medium_yellow = cv2.inRange(inner_segmented_hsv, lower_medium_yellow, upper_medium_yellow)
                    mask_bright_yellow = cv2.inRange(inner_segmented_hsv, lower_bright_yellow, upper_bright_yellow)
                    mask_brightest_yellow = cv2.inRange(inner_segmented_hsv, lower_brightest_yellow, upper_brightest_yellow)
                    mask_brightFinal_yellow = cv2.inRange(inner_segmented_hsv, lower_brightFinal_yellow, upper_brightFinal_yellow)

                    # Gabungkan semua mask
                    mask_yellow_gradient = mask_light_yellow | mask_medium_yellow | mask_bright_yellow

                    # Bersihkan mask (opsional)
                    kernel = np.ones((3, 3), np.uint8)
                    mask_yellow_gradient = cv2.morphologyEx(mask_yellow_gradient, cv2.MORPH_CLOSE, kernel)

                    # Tampilkan hasil
                    cv2.imwrite('10_GradienKuning.png', mask_yellow_gradient)

                    result = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_yellow_gradient)
                    cv2.imwrite('11_DeteksiGradien.png', result)

                    result_light_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_light_yellow)
                    result_medium_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_medium_yellow)
                    result_bright_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_bright_yellow)
                    result_brightest_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_brightest_yellow)
                    result_brightFinal_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_brightFinal_yellow)

                    cv2.imwrite('12_KuningPucat.png', result_light_yellow)
                    cv2.imwrite('13_KuningMedium.png', result_medium_yellow)
                    cv2.imwrite('14_KuningTerang.png', result_bright_yellow)
                    cv2.imwrite('15_KuningPalingTerang.png', result_brightest_yellow)
                    cv2.imwrite('16_KuningFinal.png', result_brightFinal_yellow)

                    # Total piksel dalam gambar
                    total_pixels = mask_yellow_gradient.size  # Total piksel di seluruh gambar

                    # Hitung jumlah piksel untuk setiap kategori
                    pixels_light_yellow = np.count_nonzero(mask_light_yellow)
                    pixels_medium_yellow = np.count_nonzero(mask_medium_yellow)
                    pixels_bright_yellow = np.count_nonzero(mask_bright_yellow)
                    pixels_brightest_yellow = np.count_nonzero(mask_brightest_yellow)
                    pixels_brightFinal_yellow = np.count_nonzero(mask_brightFinal_yellow)
                    pixels_yellow_gradient = np.count_nonzero(mask_yellow_gradient)

                    # Hitung persentase
                    percentage_light_yellow = (pixels_light_yellow / total_pixels) * 100
                    percentage_medium_yellow = (pixels_medium_yellow / total_pixels) * 100
                    percentage_bright_yellow = (pixels_bright_yellow / total_pixels) * 100
                    percentage_brightest_yellow = (pixels_brightest_yellow / total_pixels) * 100
                    percentage_brightFinal_Yellow = (pixels_brightFinal_yellow / total_pixels) * 100
                    percentage_yellow_gradient = (pixels_yellow_gradient / total_pixels) * 100

                    # Cetak hasil
                    print("Jumlah Piksel Kuning Pucat:", pixels_light_yellow, f"({percentage_light_yellow:.2f}%)")
                    print("Jumlah Piksel Kuning Medium:", pixels_medium_yellow, f"({percentage_medium_yellow:.2f}%)")
                    print("Jumlah Piksel Kuning Terang:", pixels_bright_yellow, f"({percentage_bright_yellow:.2f}%)")
                    print("Jumlah Piksel Kuning Paling Terang:", pixels_brightest_yellow, f"({percentage_brightest_yellow:.2f}%)")
                    print("Jumlah Piksel Kuning Paling Terang:", pixels_brightFinal_yellow, f"({percentage_brightFinal_Yellow:.2f}%)")
                    print("Jumlah Total Piksel Kuning:", pixels_yellow_gradient, f"({percentage_yellow_gradient:.2f}%)")


                    if percentage_yellow_gradient > 17.2:
                        if percentage_brightest_yellow >= 4:
                            if  percentage_medium_yellow < 3.6:
                                if 99 <= average_hue <= 103 and 226 <= average_saturation <= 245 and 91 <= average_value <= 97:
                                    Uniform = "Tajem"
                                else:
                                    Uniform = "Jablak"
                            else:
                                Uniform = "Jablak"
                        else:
                            Uniform = "Jablak"
                    elif 12 <= percentage_yellow_gradient <=17.2:
                        Uniform = "Jablak"
                    elif percentage_yellow_gradient < 12:
                        if pixels_light_yellow > 1020:
                          Uniform = "Jablak"
                        else:
                            Uniform = "Belang"
                    else:
                        Uniform = "RRQ IDOK"

                    if average_hue <= 101.8:
                        color_category = "BB"
                    elif 101.8 < average_hue <= 103.1:
                        if average_value <= 95:
                            color_category = "B"
                        else:
                            color_category = "MM"
                    elif 103.1 < average_hue <= 104.4:
                        if average_value <=95:
                            color_category = "B"
                        if 95 < average_value <= 97.7:
                            color_category = "MM"
                        else: 
                            color_category = "M"
                    elif 104.4 < average_hue <= 105.2:
                        if average_value <= 94.3:
                            color_category = "B"
                        else:  # average_value > 122
                            color_category = "M"
                    elif average_hue > 105.2:
                        color_category = "M"
                    else:
                        color_category = "Tidak Terdefinisi"



                    self.label_dimensions.config(
                        # \nWarna  :  {dominant_value}\nFrekwensi :  {domi`nant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                        text=f"Grade: {Uniform} | {color_category}\nrata2 Hue: {hue_mean:.1f}\nrata2 Saturasi: {saturation_mean:.1f}\nrata2 Value: {value_mean:.1f}\n\nH: {average_hue:.1f}\nS: {average_saturation:.1f}\nV: {average_value:.1f}"
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