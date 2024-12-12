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

# try:
#     arduino = serial.Serial('COM3', 9600, timeout=1)
#     time.sleep(2)  # Tunggu beberapa detik agar koneksi stabil
#     print("Koneksi berhasil ke Arduino!")
#     arduino.close()  # Tutup koneksi setelah pengujian
# except serial.SerialException as e:
#     print(f"Kesalahan: {e}")

class WebcamApp:
    def __init__(self, window):
        # self.arduino = serial.Serial('COM3', 9600, timeout=1)
        # time.sleep(2)  # Tunggu agar koneksi serial stabil
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
            # ========== Membaca Gambar ==========
            image = mpimg.imread(path)
            if image is None:
                print("Gambar tidak ditemukan di path:", path)
                return
            # cv2.imwrite("1. Original_Image.png", image)


            # Meningkatkan kontras dan kecerahan
            originalImage = cv2.imread(path)
            alpha = 3.2  
            beta = 0 
            enhancedImage = cv2.convertScaleAbs(originalImage, alpha=alpha, beta=beta)
            # cv2.imwrite("2. Enhanced_Image.png", enhancedImage)
            




            # ========== Deteksi Warna dan Tebal Tipis Daun Tembakau ==========
            # Konversi gambar dari BGR ke HSV
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Tentukan ukuran area untuk ekstraksi nilai (50x50)
            area_size = 175

            # Tentukan posisi untuk mengambil area 175*175
            height, width, _ = hsv_image.shape
            start_x = (width // 2) - (area_size // 2)
            start_y = (height // 2) - (area_size // 2)

            # Ekstraksi area 175x175
            hsv_area = hsv_image[start_y:start_y + area_size, start_x:start_x + area_size]

            # Memisahkan channel Hue, Saturation, dan Value
            hue_channel = hsv_area[:, :, 0]  # Channel Hue
            saturation_channel = hsv_area[:, :, 1]  # Channel Saturation
            value_channel = hsv_area[:, :, 2]  # Channel Value

            # Hitung jumlah total data Hue, Saturation, dan Value dalam area 50x50
            sum_hue = np.sum(hue_channel)
            sum_saturation = np.sum(saturation_channel)
            sum_value = np.sum(value_channel)

            # Menghitung rata-rata nilai Hue, Saturation, dan Value
            average_hue = sum_hue / (area_size * area_size)
            average_saturation = sum_saturation / (area_size * area_size)
            average_value = sum_value / (area_size * area_size)

            # Klasifikasi Kategory Warna
            color_category = self.determine_color_category(average_hue, average_value)
            # Klasifikasi Tabal Tipis
            ThicknessCategory = self.determine_thickness_category(average_saturation, average_value)
            # Menyimpan area 50x50 dan gambar HSV
            # cv2.imwrite("3. HSV Area.png", hsv_area)





            # ========== Pre Processing Citra ==========
            # Konversi gambar ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            # Segmentasi Citra Menggunakan Thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
            # Temukan Kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:

                
                # ========== Fitur Deteksi Panjang Daun Tembakau ==========
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                pixel_panjang = w
                pixel_lebar = h
                # Hitung dimensi
                panjang = 0.0895 * pixel_panjang - 3.1795
                # Tentukan kualitas daun
                kualitas = self.determine_leaf_quality(panjang)




            
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
                # cv2.imwrite('4. segmentasi Citra.png', segmented_image)
                # Temukan kontur pada gambar masker
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # Buat gambar kosong dengan ukuran yang sama dengan segmented_image
                inner_mask = np.zeros_like(mask)

                                # Pastikan ada kontur yang ditemukan
                # Pastikan ada kontur yang ditemukan
                if contours:
                    # Cari kontur terbesar
                    largest_segmented_contour = max(contours, key=cv2.contourArea)
                    
                    # Hitung parameter bentuk
                    x, y, w, h = cv2.boundingRect(largest_segmented_contour)
                    aspect_ratio = w / h
                    bounding_box_area = w * h
                    contour_area = cv2.contourArea(largest_segmented_contour)
                    extent = contour_area / bounding_box_area if bounding_box_area > 0 else 0

                    # Hitung convex hull dan solidity
                    hull = cv2.convexHull(largest_segmented_contour)
                    hull_area = cv2.contourArea(hull)
                    solidity = contour_area / hull_area if hull_area > 0 else 0

                    # Hitung circularity
                    perimeter = cv2.arcLength(largest_segmented_contour, True)
                    circularity = (4 * np.pi * contour_area) / (perimeter ** 2) if perimeter > 0 else 0

                    object_detection = self.determine_object(aspect_ratio, extent, solidity, circularity)
                else:
                    print("Tidak ada kontur pada gambar yang di-segmentasi.")



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
                # cv2.imwrite('5. result_with_inner_contour.png', result_with_inner_contour)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_RGBA2GRAY)

                    # cv2.imwrite('6. segmented_image_gray.png', segmented_image_gray)

                    
                    
                    
                    
                    # ========== Deteksi Kerusakan Daun Tembakau ==========
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
                        # cv2.imwrite('16. output_edge_detection_with_info.png', image_with_contours)

                    else:
                        print("Tidak ditemukan kontur pada gambar.")

                    # Simpan gambar yang menunjukkan hasil deteksi tepi daun
                    result_contour_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                    cv2.drawContours(result_contour_image, [largest_contour], -1, (0, 255, 0), 2)
                    # cv2.imwrite('17. contour_detection_result.png', result_contour_image)

                    # Proses 5: Tentukan rentang warna putih untuk deteksi area dalam daun
                    lower_white = np.array([253], dtype=np.uint8)
                    upper_white = np.array([255], dtype=np.uint8)
                    white_mask = cv2.inRange(segmented_image_gray, lower_white, upper_white)
                    white_pixels = cv2.countNonZero(white_mask)

                    # Cari kontur di white_mask
                    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    white_mask_bgr = cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)
                    white_mask_bgr[np.where((white_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

                    jumlah_bounding_box = 0
                    jumlah_bounding_box2 = 0
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

                        if lebar_cm > 1.4 or tinggi_cm > 1.4:
                            cv2.rectangle(white_mask_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.5
                            font_color = (0, 0, 255)
                            thickness = 1

                            text_lebar = f'L: {lebar_cm:.2f} cm'
                            cv2.putText(white_mask_bgr, text_lebar, (x, y - 10), font, font_scale, font_color, thickness)

                            text_tinggi = f'T: {tinggi_cm:.2f} cm'
                            cv2.putText(white_mask_bgr, text_tinggi, (x + w + 10, y + h // 2), font, font_scale, font_color, thickness)

                            print(f'Bounding Box {jumlah_bounding_box2 + 1}: Lebar = {lebar_cm:.2f} cm, Tinggi = {tinggi_cm:.2f} cm')
                            jumlah_bounding_box2 += 1
                        else:
                            print(f'Kontur diabaikan: Lebar = {lebar_cm:.2f} cm, Tinggi = {tinggi_cm:.2f} cm (di bawah threshold 0.5 cm)')

                    # Simpan gambar hasil deteksi lubang pada daun
                    # cv2.imwrite('18. whiteMaskBgr.png', white_mask_bgr)

                    # Ambang batas kekasaran
                    threshold_rusak = 2.25  # Nilai compactness > 1.2 dapat dianggap rusak
                    print("Compacness: ", compactness)
                    print("Thickness: ", threshold_rusak)


                    # Hitung jumlah piksel putih dan jumlah bounding box
                    white_pixels = cv2.countNonZero(white_mask)
                    print(f'Jumlah piksel putih di dalam daun: {white_pixels}')
                    print(f'Jumlah bounding box (lubang): {jumlah_bounding_box}')

                    # Gabungkan gambar BGR dengan mask kuning dan bounding box hijau
                    segmented_image_bgr = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)
                    combined_image = cv2.addWeighted(segmented_image_bgr, 0.7, white_mask_bgr, 0.3, 0)
                    # cv2.imwrite('19. gray_image.png', segmented_image_gray)

                    # Simpan gambar hasil gabungan dari deteksi kontur dan lubang
                    # cv2.imwrite('20. combined_output.png', combined_image)

                    Kerusakan = self.determine_damage_category(jumlah_bounding_box, jumlah_bounding_box2, compactness, threshold_rusak)



                    inner_segmented_hsv= cv2.cvtColor(result_with_inner_contour, cv2.COLOR_BGR2HSV)
                  
                    segmented_image_hsv = cv2.cvtColor(inner_segmented_hsv, cv2.COLOR_BGR2HSV)
                    # cv2.imwrite('9. Image_Inner_HSV.png', segmented_image_hsv)
                    
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
                    # cv2.imwrite('10. blockingHSV.png', blocked_image)

                    # Pisahkan channel H, S, V
                    hue_channel = inner_segmented_hsv[:, :, 0]
                    saturation_channel = inner_segmented_hsv[:, :, 1]
                    value_channel = inner_segmented_hsv[:, :, 2]            

                    inner_segmented_hsv = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_BGR2HSV)

                    # Definisikan rentang untuk berbagai tingkatan kuning
                    lower_light_yellow = np.array([20, 50, 150])  # Kuning pucat
                    upper_light_yellow = np.array([30, 200, 255])

                    lower_medium_yellow = np.array([25, 100, 100])  # Kuning medium
                    upper_medium_yellow = np.array([35, 255, 255])

                    lower_bright_yellow = np.array([30, 100, 100])  # Kuning terang
                    upper_bright_yellow = np.array([40, 255, 255])

                    
                    lower_brown = np.array([20, 50, 150])  # Kuning terang
                    upper_brown = np.array([30, 150, 255])

                    # Mask untuk setiap gradien
                    mask_light_yellow = cv2.inRange(inner_segmented_hsv, lower_light_yellow, upper_light_yellow)
                    mask_medium_yellow = cv2.inRange(inner_segmented_hsv, lower_medium_yellow, upper_medium_yellow)
                    mask_bright_yellow = cv2.inRange(inner_segmented_hsv, lower_bright_yellow, upper_bright_yellow)
                    mask_brown = cv2.inRange(inner_segmented_hsv, lower_brown, upper_brown)

                    # Gabungkan semua mask
                    mask_yellow_gradient = mask_light_yellow | mask_medium_yellow | mask_bright_yellow

                    # Bersihkan mask (opsional)
                    kernel = np.ones((3, 3), np.uint8)
                    mask_yellow_gradient = cv2.morphologyEx(mask_yellow_gradient, cv2.MORPH_CLOSE, kernel)

                    # Total piksel dalam gambar
                    total_pixels = mask_yellow_gradient.size  # Total piksel di seluruh gambar

                    # Hitung jumlah piksel untuk setiap kategori
                    pixels_light_yellow = np.count_nonzero(mask_light_yellow)
                    pixels_medium_yellow = np.count_nonzero(mask_medium_yellow)
                    pixels_bright_yellow = np.count_nonzero(mask_bright_yellow)
                    pixels_yellow_gradient = np.count_nonzero(mask_yellow_gradient)
                    pixels_brown = np.count_nonzero(mask_brown)

                    # Hitung persentase
                    percentage_light_yellow = (pixels_light_yellow / total_pixels) * 100
                    percentage_medium_yellow = (pixels_medium_yellow / total_pixels) * 100
                    percentage_bright_yellow = (pixels_bright_yellow / total_pixels) * 100
                    percentage_yellow_gradient = (pixels_yellow_gradient / total_pixels) * 100
                    percentage_brown = (pixels_brown / total_pixels) * 100

                    # Cetak hasil
                    print("Jumlah Piksel Kuning Pucat:", pixels_light_yellow, f"({percentage_light_yellow:.2f}%)")
                    print("Jumlah Piksel Kuning Medium:", pixels_medium_yellow, f"({percentage_medium_yellow:.2f}%)")
                    print("Jumlah Piksel Kuning Terang:", pixels_bright_yellow, f"({percentage_bright_yellow:.2f}%)")
                    print("Jumlah Total Piksel Kuning:", pixels_yellow_gradient, f"({percentage_yellow_gradient:.2f}%)")
                    print("Jumlah Total Piksel Kuning:", pixels_brown, f"({percentage_brown:.2f}%)")

                    # Simpan hasil gambar
                    # cv2.imwrite('11. GradienKuning.png', mask_yellow_gradient)
                    result = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_yellow_gradient)
                    # cv2.imwrite('12_DeteksiGradien.png', result)

                    result_light_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_light_yellow)
                    result_medium_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_medium_yellow)
                    result_bright_yellow = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_bright_yellow)
                    result_brown = cv2.bitwise_and(result_with_inner_contour, result_with_inner_contour, mask=mask_brown)

                    # cv2.imwrite('13_KuningPucat.png', result_light_yellow)
                    # cv2.imwrite('14_KuningMedium.png', result_medium_yellow)
                    # cv2.imwrite('15_KuningTerang.png', result_bright_yellow)
                    # cv2.imwrite('15_Coklat.png', result_brown)

                    Uniform = self.determine_uniform_category(percentage_yellow_gradient, percentage_light_yellow)

                    if pixels_light_yellow <= 10:
                        Status = 0
                    else :
                        Status = 1




                    # ========== Deteksi Minyak Daun Tembakau ==========
                    # Tentukan rentang warna hitam (minyak)
                    # Rentang untuk warna hitam
                    lower_black = np.array([60], dtype=np.uint8)
                    upper_black = np.array([80], dtype=np.uint8)

                    # Buat mask untuk warna hitam
                    black_mask = cv2.inRange(segmented_image_gray, lower_black, upper_black)
                    black_pixels = cv2.countNonZero(black_mask)

                    # Hitung total piksel
                    total_pixels = segmented_image_gray.size

                    # Hitung persentase piksel hitam
                    black_percentage = (black_pixels / total_pixels) * 100

                    # Ganti piksel hitam dengan warna kuning pada gambar BGR
                    black_mask_bgr = cv2.cvtColor(black_mask, cv2.COLOR_GRAY2BGR)
                    black_mask_bgr[np.where((black_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 255, 255]  # Warna kuning
                    # cv2.imwrite('21. blackMaskBgr.png', black_mask_bgr)

                    # Cetak hasil
                    print(f"Black Pixels: {black_pixels}")
                    print(f"Black Percentage: {black_percentage:.2f}%")

                    oil_category = self.determine_oil_category(black_pixels, black_percentage)

                    determine_object = self.determine_object(panjang, average_hue, average_saturation, average_value)

                    # Mengirim data ke Arduino
                    # grading = f"{kualitas}|{color_category}|{Kerusakan}|M{oil_category}|{Uniform}" 
                    # self.send_hue_and_color_category(Status, grading)
                    # if determine_object == 1:
                    # self.label_dimensions.config(
                    #     text=f"Grade:\n {kualitas} | {color_category} | {Kerusakan} | M{oil_category} | {Uniform} \nKetebalan: {ThicknessCategory}\nRasio: {aspect_ratio:.1f}\nExtent: {extent:.1f},Solidity: {solidity:.1f}\nCircularity: {circularity:.1f} "
                    #     )
                    if object_detection == 1:
                        self.label_dimensions.config(
                        text=f"Grade:\n {kualitas} | {color_category} | {Kerusakan} | M{oil_category} | {Uniform} \nKetebalan: {ThicknessCategory}\nH: {average_hue:.1f}\nS: {average_saturation:.1f}\nV: {average_value:.1f}"
                        )
                    else: 
                        self.label_dimensions.config(
                            text=f"Grade:\n Tidak ada Daun"
                        )
                else: 
                    print("Segmented Not Found")
            else:
                print("Contour Not Found")
        else:
            print("Image path not found.")

    # def send_hue_and_color_category(self, hue_value, color_category):
    #     data = f"{hue_value},{color_category}\n"
    #     self.arduino.write(data.encode())  # Kirim data ke Arduino
    #     print(f"Data dikirim: {data.strip()}")



    def determine_object(self, aspect_ratio, extent, solidity, circularity):
        if 1.2 < aspect_ratio < 2.4:
            if 0.5 <= extent < 0.8:
                if 0.8 <= solidity <= 1.1:
                    if 0.4 < circularity <= 0.8:
                        return 1
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0 


    def determine_leaf_quality(self, panjang):
        print(f"Panjang daun: {panjang}")
        if panjang < 5:
            return "-"
        elif panjang > 45.1:
            print("Masuk kategori Super")
            return "Super"
        elif 40.1 <= panjang <= 45.1:
            print("Masuk kategori Lente 1")
            return "L1"
        elif 35.1 <= panjang < 40.1:
            print("Masuk kategori Lente 2")
            return "L2"
        elif 29.8 <= panjang < 35.1:
            print("Masuk kategori Lente 3")
            return "L3"
        else:
            print("Masuk kategori Filler")
            return "Filler"

    def determine_color_category(self, average_hue, average_value):
        if average_hue <= 101.8:
            return "BB"
        elif 101.8 < average_hue <= 103.1:
            if average_value <= 95:
                return "B"
            else:
                return "MM"
        elif 103.1 < average_hue <= 104.4:
            if average_value <=95:
                return "B"
            if 95 < average_value <= 97.7:
                return "MM"
            else: 
                return "M"
        elif 104.4 < average_hue <= 105.2:
            if average_value <= 94.3:
                return "B"
            else:  # average_value > 122
                return "M"
        elif average_hue > 105.2:
            return "M"
        else:
            return "Tidak Terdefinisi"
        
    
    def determine_thickness_category(self, average_saturation, average_value):
        if average_saturation <= 70 :
            if average_value >= 150: 
                return "Tipis"
            else:
                return "Sedang"
        elif 70 < average_saturation <= 91:
            if average_value >= 155:
                return "Tipis"
            else: 
                return "Sedang"
        elif 91 < average_saturation <=200:
            if average_value >= 150: 
                return  "Sedang"
            else:
                return "Tebal"
        else :
            return "Tebal" 
        
    def determine_oil_category(self, black_pixels, black_percentage):
        if black_pixels == 0:
            return 0
        elif black_pixels <= 1500:
            return 2
        elif 1500 <= black_pixels <= 2100:
            return 3
        elif black_pixels > 2100:
            return 4
        else:
            return 0
        
    def determine_damage_category(self, jumlah_bounding_box, jumlah_bounding_box2, compactness, threshold_rusak):
        if jumlah_bounding_box == 0 and compactness <= threshold_rusak:
            return "Utuh"
        elif 0 < jumlah_bounding_box <= 4 and compactness <= threshold_rusak and jumlah_bounding_box2 == 0:
            return "r"
        elif compactness > threshold_rusak and jumlah_bounding_box == 0 and jumlah_bounding_box2 == 0:
            return "r"
        elif jumlah_bounding_box >= 7:
            return "R1"
        elif jumlah_bounding_box2 >= 1:
            return "R1"
        elif compactness > threshold_rusak and (jumlah_bounding_box >= 5 or jumlah_bounding_box2 >= 1):
            return "R1"
        elif compactness > threshold_rusak:
            return "R1"
        else:
            return "R1"
        
    def determine_uniform_category(self, percentage_yellow_gradient, percentage_light_yellow):
        if percentage_yellow_gradient >= 7.4:
            if percentage_light_yellow >= 2.45:
                if percentage_yellow_gradient >=31:
                    return "Tajem"
                else:
                    return "Jablak"
            else:
                return "Belang"
        else:
            return "Belang"          
    
root = tk.Tk()
app = WebcamApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()