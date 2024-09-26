import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
import serial
import time
import matplotlib.image as mpimg

# # Setup komunikasi serial
# try:
#     ser = serial.Serial('COM3', 9600)  # Ganti 'COM3' dengan port serial Arduino Anda
# except serial.SerialException as e:
#     print(f"Error opening serial port: {e}")
#     ser = None

# # Inisialisasi variabel global di luar fungsi
# previous_oil_category = None
# start_time = time.time()

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

            # Debug print statements
            print(f"Average Hue: {average_hue}")
            print(f"Average Saturation: {average_saturation}")
            print(f"Average Value: {average_value}")

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

                # Hitung dimensi
                panjang = 0.1101 * w - 6.882

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

                # Konversi citra tersegmentasi ke grayscale jika perlu
                if len(segmented_image.shape) == 3:
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)

                    # Tentukan rentang warna putih
                    lower_white = np.array([130], dtype=np.uint8)
                    upper_white = np.array([255], dtype=np.uint8)
                    
                    # Buat mask untuk warna putih
                    white_mask = cv2.inRange(segmented_image_gray, lower_white, upper_white)
                    white_pixels = cv2.countNonZero(white_mask)

                    # Ganti piksel putih dengan warna kuning pada gambar BGR
                    white_mask_bgr = cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)
                    white_mask_bgr[np.where((white_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]
                    cv2.imwrite('whiteMaskBgr.png', white_mask_bgr)
                    cv2.imwrite('whiteMaskBgr.png', white_mask_bgr)
                    white_pixels = cv2.countNonZero(white_mask)
                    print(f'Jumlah piksel putih di dalam daun: {white_pixels}')

                    if (white_pixels < 20):
                        Kerusakan = "Utuh"
                    else:
                        Kerusakan = "Rambing"

                    # Ubah gambar grayscale menjadi BGR
                    segmented_image_bgr = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)

                    # Gabungkan gambar BGR dengan mask kuning
                    combined_image = cv2.addWeighted(segmented_image_bgr, 0.7, white_mask_bgr, 0.3, 0)

                    # Simpan gambar hasil gabungan
                    cv2.imwrite('combined_output.png', combined_image)

                    # Tentukan rentang warna hitam (minyak)
                    lower_black = np.array([1], dtype=np.uint8)
                    upper_black = np.array([40], dtype=np.uint8)

                    # Buat mask untuk warna hitam
                    black_mask = cv2.inRange(segmented_image_gray, lower_black, upper_black)
                    black_pixels = cv2.countNonZero(black_mask)

                    # Tentukan nilai smoothing factor alpha (nilai antara 0 dan 1, lebih kecil = lebih halus)
                    alpha = 0.1

                    # Variabel untuk menyimpan nilai black_pixels yang telah dinormalisasi
                    smoothed_black_pixels = 0

                    # Hitung jumlah piksel hitam
                    black_pixels = cv2.countNonZero(black_mask)

                    # Terapkan exponential smoothing
                    smoothed_black_pixels = alpha * black_pixels + (1 - alpha) * smoothed_black_pixels
                    # Membulatkan nilai smoothed_black_pixels ke bilangan bulat
                    smoothed_blackpixels = int(round(smoothed_black_pixels))
                    print(f"Smoothed black pixels: {smoothed_blackpixels}")


                    # Ganti piksel hitam dengan warna kuning pada gambar BGR
                    black_mask_bgr = cv2.cvtColor(black_mask, cv2.COLOR_GRAY2BGR)
                    black_mask_bgr[np.where((black_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]
                    cv2.imwrite('blackMaskBgr.png', black_mask_bgr)
                    print(black_pixels)

                    # Hitung jumlah piksel untuk setiap nilai intensitas dari 0 hingga 255
                    pixel_counts = np.bincount(segmented_image_gray.flatten(), minlength=256)

                    # Tentukan rentang warna dari 1 hingga 255
                    lower_range = np.array([1], dtype=np.uint8)
                    upper_range = np.array([255], dtype=np.uint8)

                    # Buat mask untuk rentang warna
                    range_mask = cv2.inRange(segmented_image_gray, lower_range, upper_range)
                    range_pixels = cv2.countNonZero(range_mask)

                    # # Bagian di mana Anda menentukan kategori minyak
                    # global previous_oil_category, start_time
                    
                    # Tentukan kategori minyak 

                    # normalisasiBlackpixel = black_pixels / 20

                    # if normalisasiBlackpixel == 0:
                    #     oil_category = 0
                    # elif normalisasiBlackpixel <= 20:
                    #     oil_category = 2
                    # elif 20 < normalisasiBlackpixel <= 130:
                    #     oil_category = 3
                    # elif normalisasiBlackpixel > 130:
                    #     oil_category = 4
                    # else:
                    #     oil_category = 0


                    if black_pixels == 0:
                        oil_category = 0
                    elif black_pixels <= 254:
                        oil_category = 2
                    elif 205 <= black_pixels <= 1320:
                        oil_category = 3
                    elif black_pixels > 1500:
                        oil_category = 4
                    else:
                        oil_category = 0

                    # Tentukan kategori warna berdasarkan average_hue dan average_value
                    if average_hue <= 106.2:
                        if average_value <= 119:
                            color_category = "BB"
                        else:
                            color_category = "MM"
                    elif 106.2 < average_hue <= 107.2:
                        if average_value <= 106:
                            color_category = "B"
                        elif 106 < average_value <= 112:
                            color_category = "BB"
                        else:  
                            color_category = "MM"
                    elif 107.2 < average_hue <= 108.2:
                        if average_value <= 106:
                            color_category = "B"
                        elif 106 < average_value <= 121:
                            color_category = "MM"
                        else:  # average_value > 122
                            color_category = "M"
                    elif average_hue > 108.2:
                        color_category = "M"
                    else:
                        color_category = "Tidak Terdefinisi"



                    # # Tentukan kategori warna berdasarkan average_hue dan oil_category
                    # if average_hue <= 106.2:
                    #     color_category = "BB"
                    # elif 106.2 < average_hue <= 107.2 and average_value > 106:
                    #     color_category = "BB"
                    # elif 106.2 < average_hue <= 107.2 and average_value <= 106:
                    #     color_category = "B"
                    # elif 107.2 < average_hue <= 108.2 and average_value <= 106:
                    #     color_category = "B"
                    # elif 107.2 < average_hue <= 108.2 and 106 < average_value <= 122:
                    #     color_category = "MM"
                    # elif 107.2 < average_hue <= 108.2 and average_value > 122:
                    #     color_category = "M"
                    # elif average_hue > 108.2:
                    #     color_category = "M"
                    # else:
                    #     color_category = "Tidak Terdefinisi"



                    # if average_hue <= 107 and black_pixels <= 130:
                    #     color_category = "BB"
                    # elif average_hue > 107 and black_pixels <= 130:
                    #     color_category = "MM"
                    # #     elif 110 <= average_hue <= 111.6 and black_pixels >= 131:
                    # #     color_category = "B"

                    # elif average_hue < 140 and 131 <= black_pixels <= 204:
                    #     color_category = "MM"

                    # #     color_category = "M"
                    # elif average_hue < 130 and 205 <= black_pixels <= 600:
                    #     color_category = "MM"
                    # # elif average_hue >= 108 and 205 <= black_pixels <= 600:
                    # #     color_category = "M"

                    # elif average_hue < 108 and 601 <= black_pixels <= 1300:
                    #     color_category = "MM"
                    # elif average_hue >= 108 and 601 <= black_pixels <= 1300:
                    #     color_category = "M"

                    # elif average_hue <= 107 and black_pixels >= 1301 :
                    #     color_category = "B"

                    # elif average_hue > 108.1 and 1301 <= black_pixels <= 1899:
                    #     color_category = "M"
                    # elif 107 < average_hue >= 108 and black_pixels <= 1900:
                    #     color_category = "MM"
                    # elif 107 < average_hue >= 108 and black_pixels > 1900:
                    #     color_category = "M"
                    # elif average_hue > 107 and black_pixels >= 1901:
                    #     color_category = "M"
                    # else:
                    #     color_category = "Tidak Terdefinisi"

                    # print("Kategori warna:", color_category)
 
                    # # Debug print statements
                    # print(f'Current oil_category: {oil_category}')
                    # print(f'Previous oil_category: {previous_oil_category}')

                    # Penentuan kategori warna berdasarkan rentang penyetaraanHue
                    # if black_pixels == 0:
                    #     kategoriWarna = "-"
                    # elif black_pixels < 80:
                    #     kategoriWarna = "BB"
                    # elif penyetaraanHue <= 0.3 and 80 <= black_pixels <= 120:ssssssss
                    #     kategoriWarna = 'BB'
                    # elif penyetaraanHue > 0.3 and 80 <= black_pixels <= 120:
                    #     kategoriWarna = 'MM'
                    # elif  penyetaraanHue <= 0.305  and 120 <= black_pixels < 1800 :
                    #     kategoriWarna = 'MM'
                    # elif penyetaraanHue > 0.305  and 120 <= black_pixels < 1800 :
                    #     kategoriWarna = 'M'
                    # else:
                    #     kategoriWarna = 'M'

                    # print(f"Kategori Warna: {kategoriWarna}")



                    # if black_pixels == 0:
                    #     kategoriWarna = "-"
                    # elif black_pixels < 80:
                    #     kategoriWarna = "BB"
                    # elif penyetaraanHue <= 0.3 and 80 <= black_pixels <= 120:
                    #     kategoriWarna = 'BB'
                    # elif penyetaraanHue > 0.3 and 80 <= black_pixels <= 120:
                    #     kategoriWarna = 'MM'
                    # elif  penyetaraanHue <= 0.307  and 120 <= black_pixels <= 800 :
                    #     kategoriWarna = 'MM'
                    # elif penyetaraanHue > 0.307  and 120 <= black_pixels <= 800 :
                    #     kategoriWarna = 'M'

                    # elif  penyetaraanHue <= 0.305  and 800 <= black_pixels <= 1350 :
                    #     kategoriWarna = 'MM'

                    
                    # elif 0.305 <= penyetaraanHue <= 0.318  and 800 <= black_pixels <= 1350 :
                    #     kategoriWarna = 'M'
                    
                    # elif penyetaraanHue <= 0.318  and black_pixels > 1350 :
                    #     kategoriWarna = 'B'
                    # else:
                    #     kategoriWarna = 'M'

                    # print(f"Kategori Warna: {kategoriWarna}")


                    sent_signal = False  # Tambahkan flag untuk melacak pengiriman sinyal

                    # if oil_category == previous_oil_category:
                    #     if time.time() - start_time >= 3 and not sent_signal:  # Jika kategori tidak berubah lebih dari 3 detik dan belum dikirim
                    #         print("Sending blink signal to Arduino")  # Debug print
                    #         ser.write(f'S:{kualitas} | M{oil_category} | {color_category}\n'.encode())  # Kirim sinyal 'S' dan kualitas daun ke Arduino
                    #         sent_signal = True  # Set flag menjadi True setelah pengiriman
                    # else:
                    #     previous_oil_category = oil_category
                    #     start_time = time.time()  # Reset timer hanya saat nilai berubah
                    #     sent_signal = False  # Reset flag jika kategori berubah
                    #     print("Category changed, resetting timer")


                    PanjangDaun = max(panjang, 0)
                    # self.label_dimensions.config(
                    #     # \nWarna  :  {dominant_value}\nFrekwensi :  {dominant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                    #     text=f"Kualitas daun: {kualitas}\nKategori Minyak = M{oil_category}\nBanyak Pixel : {black_pixels}\nKategoriWarna : {kategoriWarna}"
                    # )
                    print("Daun :", Kerusakan)
                    # self.label_dimensions.config(
                    #     # \nWarna  :  {dominant_value}\nFrekwensi :  {dominant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                    #     text=f"Panjang daun: {PanjangDaun:.1f} cm\nPanjang Px: {w}\nKualitas daun: {kualitas}\nKategori Minyak = M{oil_category}\nBanyak Pixel : {black_pixels}\nHue: {average_hue:.1f}\nSaturasi: {average_saturation:.1f}\nValue: {average_value:.1f}\nPH: {penyetaraanHue:3f}\nPS: {penyetaraanSaturation:.3f}\nKategoriWarna : {kategoriWarna}\nKerusakan : {Kerusakan}"
                    # )
                    self.label_dimensions.config(
                        # \nWarna  :  {dominant_value}\nFrekwensi :  {domi`nant_frequency}\nKerusakan :  {percentageKerusakan:.2f}%
                        text=f"Grade:\n {kualitas} | {color_category}"

                    )
              
                else: 
                    print("Segmented Not Found")
            else:
                print("Contour Not Found")
        else:
            print("Image path not found.")

    def determine_leaf_quality(self, panjang):
        print(f"Panjang daun: {panjang}")
        if panjang < 5:
            return "-"
        elif panjang > 45:
            print("Masuk kategori Super")
            return "Super"
        elif 40.3 <= panjang <= 45:
            print("Masuk kategori Lente 1")
            return "Lente 1"
        elif 35.5 <= panjang < 40.3:
            print("Masuk kategori Lente 2")
            return "Lente 2"
        elif 30 <= panjang < 35.5:
            print("Masuk kategori Lente 3")
            return "Lente 3"
        else:
            print("Masuk kategori Filler")
            return "Filler"


root = tk.Tk()
app = WebcamApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()