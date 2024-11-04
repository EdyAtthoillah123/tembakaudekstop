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

            if image is None:
                print("Gambar tidak ditemukan di path:", path)
                return

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
                        # Mengirimkan nilai rata-rata Hue ke Arduino

            normalisasiHue = average_hue / 360
            normalisasiSaturation = average_saturation / 255
            normalisasiValue = average_value / 255
            penyetaraanHue = normalisasiHue + 0.01 * ((0.75 - normalisasiValue) / normalisasiValue)
            penyetaraanSaturation = normalisasiSaturation * (0.75 * normalisasiValue)

            print(f"Penyetaraan Hue: {penyetaraanHue:.3f}")
            print(f"Penyetaraan Saturation: {penyetaraanSaturation:.3f}")

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
                panjang = 0.0968 * pixel_panjang - 3.4385

                # Tentukan kualitas daun
                kualitas = self.determine_leaf_quality(panjang)

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

                # Temukan kontur pada gambar masker
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Buat gambar kosong dengan ukuran yang sama dengan segmented_image
                inner_mask = np.zeros_like(mask)

                # Loop melalui setiap kontur yang ditemukan
                for contour in contours:
                    # Shrink kontur ke dalam dengan jarak 50 piksel menggunakan offset
                    offset_distance = 40

                    # Buat offset dengan -50 piksel ke dalam menggunakan `cv2.drawContours`
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
                    # Menggunakan Gaussian Blur sebelum deteksi tepi

                    inner_segmented_gray = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('Inner_Segmented_Gray.png', inner_segmented_gray)
                    
                    # Tentukan rentang warna hitam (minyak)
                    lower_black = np.array([5], dtype=np.uint8)
                    upper_black = np.array([40], dtype=np.uint8)

                    # Buat mask untuk warna hitam
                    black_mask = cv2.inRange(inner_segmented_gray, lower_black, upper_black)
                    
                    # Deteksi tepi dengan Canny untuk menemukan tulang daun
                    edges = cv2.Canny(inner_segmented_gray, 50, 150)
                    cv2.imwrite('edges.png', edges)

                    # Dilatasi untuk mempertebal tepi tulang daun
                    kernel = np.ones((1, 1), np.uint8)
                    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
                    cv2.imwrite('dilated_edges.png', dilated_edges)

                    # Buat mask tulang daun
                    leaf_veins_mask = cv2.bitwise_not(dilated_edges)
                    cv2.imwrite('leaf_veins_mask.png', leaf_veins_mask)

                    # Terapkan leaf_veins_mask pada black_mask agar tulang daun tidak ikut terdeteksi sebagai minyak
                    filtered_black_mask = cv2.bitwise_and(black_mask, black_mask, mask=leaf_veins_mask)
                    black_pixels_filtered = cv2.countNonZero(filtered_black_mask)

                    # Ganti piksel hitam (minyak) dengan warna kuning pada gambar BGR
                    filtered_black_mask_bgr = cv2.cvtColor(filtered_black_mask, cv2.COLOR_GRAY2BGR)
                    filtered_black_mask_bgr[np.where((filtered_black_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 255, 255]
                    cv2.imwrite('filtered_blackMaskBgr.png', filtered_black_mask_bgr)

                    print("Jumlah piksel hitam setelah filter tulang daun:", black_pixels_filtered)

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
                    threshold_rusak = 2  # Nilai compactness > 1.2 dapat dianggap rusak
                    print("Compacness: ", compactness)
                    print("Thickness: ", threshold_rusak)

                    if jumlah_bounding_box >= 1 and compactness <= threshold_rusak:
                        Kerusakan = "Rambing"
                    elif compactness > threshold_rusak and jumlah_bounding_box == 0:
                        Kerusakan = "Rambing"
                    elif compactness > threshold_rusak and jumlah_bounding_box >= 1:
                        Kerusakan = "Rambing"
                    elif jumlah_bounding_box == 0 and compactness <= threshold_rusak:
                        Kerusakan = "Utuh"
                    else:
                        Kerusakan = "Utuh"
                    

                    # Hitung jumlah piksel putih dan jumlah bounding box
                    white_pixels = cv2.countNonZero(white_mask)
                    print(f'Jumlah piksel putih di dalam daun: {white_pixels}')
                    print(f'Jumlah bounding box (lubang): {jumlah_bounding_box}')

                    # Gabungkan gambar BGR dengan mask kuning dan bounding box hijau
                    segmented_image_bgr = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)
                    combined_image = cv2.addWeighted(segmented_image_bgr, 0.7, white_mask_bgr, 0.3, 0)
                    cv2.imwrite('gray_image.png', segmented_image_gray)

                    # Simpan gambar hasil gabungan dari deteksi kontur dan lubang
                    cv2.imwrite('9_combined_output.png', combined_image)
                    # Hitung jumlah piksel untuk setiap nilai intensitas dari 0 hingga 255
                    pixel_counts = np.bincount(segmented_image_gray.flatten(), minlength=256)

                    # Tentukan rentang warna dari 1 hingga 255
                    lower_range = np.array([1], dtype=np.uint8)
                    upper_range = np.array([255], dtype=np.uint8)

                    # Buat mask untuk rentang warna
                    range_mask = cv2.inRange(segmented_image_gray, lower_range, upper_range)
                    range_pixels = cv2.countNonZero(range_mask)

                    if black_pixels_filtered == 0:
                        oil_category = 0
                    elif black_pixels_filtered <= 1850:
                        oil_category = 2
                    elif 1850 <= black_pixels_filtered <= 2650:
                        oil_category = 3
                    elif black_pixels_filtered > 2650:
                        oil_category = 4
                    else:
                        oil_category = 0

                    if average_hue <= 101.4:
                        color_category = "BB"
                    elif 101.4 < average_hue <= 102.7:
                        if average_value <= 91:
                            color_category = "B"
                        else:
                            color_category = "MM"
                    elif 102.7 < average_hue <= 103.9:
                        if average_value <=91:
                            color_category = "B"
                        else: 
                            color_category = "MM"
                    elif 103.9 < average_hue <= 104.8:
                        if average_value <= 90.3:
                            color_category = "B"
                        else:  # average_value > 122
                            color_category = "M"
                    elif average_hue > 104.8:
                        color_category = "M"
                    else:
                        color_category = "Tidak Terdefinisi"


                    PanjangDaun = max(panjang, 0)
                    # Mengirim data ke Arduino
                    # Kategori warna berdasarkan average_hue dan average_value

                    # Format string yang ingin dikirim
                    grading = f"{kualitas}|{color_category}|{Kerusakan}|M{oil_category}" 
                    self.send_hue_and_color_category(average_hue, grading)
  # Tampilkan nilai hue dan kategori warna
                    
                    self.label_dimensions.config(
                        # \nWarna  :  {dominant_value}\nFrekwensi :  {domi`nant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                        text=f"Grade:\n {kualitas} | {color_category} | {Kerusakan} | M{oil_category} \nPanjang Asli: {panjang:.1f}\nPanjang: {pixel_panjang}\nLebar: {pixel_lebar}\nHue : {average_hue:.1f}\nSaturation : {average_saturation:.1f}\nValue : {average_value:.1f}\nPixel: {black_pixels_filtered}\nC: {compactness:1f}\nT:{threshold_rusak}"

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

    def determine_leaf_quality(self, panjang):
        print(f"Panjang daun: {panjang}")
        if panjang < 5:
            return "-"
        elif panjang > 45.1:
            print("Masuk kategori Super")
            return "Super"
        elif 40.1 <= panjang <= 45.1:
            print("Masuk kategori Lente 1")
            return "Lente 1"
        elif 35.1 <= panjang < 40.1:
            print("Masuk kategori Lente 2")
            return "Lente 2"
        elif 29.8 <= panjang < 35.1:
            print("Masuk kategori Lente 3")
            return "Lente 3"
        else:
            print("Masuk kategori Filler")
            return "Filler"


root = tk.Tk()
app = WebcamApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()