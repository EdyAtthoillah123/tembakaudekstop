import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import rgb2gray
import matplotlib.image as mpimg


import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import mysql.connector

class WebcamApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Webcam App")

        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)
        self.current_image = None  # Ensure current_image is initialized

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
            window, text="Capture", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c",
            activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
            command=self.download_image
        )
        self.button_capture.grid(row=1, column=0, pady=20, padx=20)

        # Close Button with hover effect
        self.button_close = tk.Button(
            window, text="Close", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c",
            activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
            command=window.quit
        )
        self.button_close.grid(row=1, column=1, pady=20, padx=20)

        self.button_close.bind("<Enter>", self.on_enter)
        self.button_close.bind("<Leave>", self.on_leave)

        # Start video loop
        self.update_frame()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas_webcam.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(10, self.update_frame)

    def on_closing(self):
        self.video_capture.release()
        self.window.destroy()

    def on_enter(self, e):
        e.widget['bg'] = '#d35400'

    def on_leave(self, e):
        e.widget['bg'] = '#e74c3c'

    def download_image(self):
        if self.current_image is not None:
            directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Ambil nama gambar terakhir dan buat nama baru yang unik
            image_name = self.generate_unique_image_name()

            file_path = os.path.join(directory, image_name)
            self.current_image.save(file_path)
            
            # Simpan nama file ke database
            self.save_image_name_to_db(image_name)

            # Process the saved image
            self.process_image(file_path)
        else:
            print("No image to save!")

    def generate_unique_image_name(self):
        # Koneksi ke database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="your_database_name"
        )
        cursor = conn.cursor()
        
        # Ambil nama gambar terakhir
        cursor.execute("SELECT image_name FROM images ORDER BY id DESC LIMIT 1")
        last_image = cursor.fetchone()
        
        # Tentukan nomor untuk nama gambar berikutnya
        if last_image:
            last_image_name = last_image[0]
            last_number = int(last_image_name.split("_")[1].split(".")[0])
            new_number = last_number + 1
        else:
            new_number = 1
        
        # Buat nama gambar baru
        new_image_name = f"captured_image_{new_number}.jpg"
        
        # Tutup koneksi database
        cursor.close()
        conn.close()
        
        return new_image_name

    def save_image_name_to_db(self, image_name):
        # Koneksi ke database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="klasifikasi_tembakau"
        )
        cursor = conn.cursor()
        
        # Simpan nama gambar ke tabel
        query = "INSERT INTO images (image_name) VALUES (%s)"
        cursor.execute(query, (image_name,))
        
        # Commit dan tutup koneksi
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Image name '{image_name}' saved to database.")

    def process_image(self, path):
        if os.path.exists(path):
            image = mpimg.imread(path)
            plt.imshow(image)
            plt.title("Processed Image")
            plt.axis("off")
            plt.show()
            
            # Konversi Image Ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

                    # Hitung histogram dari gambar grayscale
            histogram = cv2.calcHist([img_gray], [0], None, [256], [0, 256]).flatten()
            
            # Temukan nilai piksel dominan
            dominant_value = np.argmax(histogram)
            dominant_frequency = histogram[dominant_value]

            # Segmentasi Citra Menggunakan Thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
            
            # Temukan Kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Hitung dimensi
                panjang = 0.0154 * w - 0.165
                lebar = 0.0151 * h - 0.0715
                PixelPanjang = w
                PixelLebar = h

                 # Tentukan kualitas daun
                kualitas = self.determine_leaf_quality(panjang)

                # Deteksi kerusakan dan minyak 
                x, y, w, h = cv2.boundingRect(largest_contour)

                cropped_image = image[y:y+h, x:x+w]
                plt.imshow(cropped_image)
                plt.savefig('imageCropped.png')  
                plt.close()
                
                # Buat masker untuk citra yang dipotong
                mask = np.zeros((h, w), dtype=np.uint8)
                plt.imshow(mask)
                plt.savefig('imageMask.png')  
                plt.close()
                
                # Sesuaikan koordinat kontur ke citra yang dipotong
                adjusted_contour = largest_contour - [x, y]
                
                # Isi area kontur pada masker
                cv2.drawContours(mask, [adjusted_contour], -1, (255), thickness=cv2.FILLED)
                
                # Segmentasikan objek dengan masker
                segmented_image = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
                plt.imshow(segmented_image)
                plt.savefig('imageSegmented.png')  
                plt.close()

                # Konversi citra tersegmentasi ke grayscale jika perlu
                if len(segmented_image.shape) == 3:
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('segmentedImageGray.png', segmented_image_gray)

                    # Tentukan rentang warna putih
                    lower_white = np.array([130 ], dtype=np.uint8)
                    upper_white = np.array([255], dtype=np.uint8)
                    # Buat mask untuk warna putih
                    white_mask = cv2.inRange(segmented_image_gray, lower_white, upper_white)

                    # Ubah mask menjadi gambar berwarna (BGR)
                    white_mask_bgr = cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)

                    # Ganti piksel putih dengan warna kuning
                    white_mask_bgr[np.where((white_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]
                    cv2.imwrite('whiteMaskBgr.png', white_mask_bgr)

                    white_pixels = cv2.countNonZero(white_mask)
                    print(f'Jumlah piksel putih di dalam daun: {white_pixels}')

                    if (white_pixels > 250):
                        print("Kualitas daun Rusak")
                    else:
                        print("Kualitas daun Bagus")

                    # Ubah gambar grayscale menjadi BGR
                    segmented_image_bgr = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)

                    # Gabungkan gambar BGR dengan mask kuning
                    combined_image = cv2.addWeighted(segmented_image_bgr, 0.7, white_mask_bgr, 0.3, 0)

                    # Simpan gambar hasil gabungan
                    cv2.imwrite('combined_output.png', combined_image)

                    
                    # Tentukan rentang warna putih
                    lower_black = np.array([1], dtype=np.uint8)
                    upper_black = np.array([50], dtype=np.uint8)

                    
                    # Buat mask untuk warna putih
                    black_mask = cv2.inRange(segmented_image_gray, lower_black, upper_black)

                    # Ubah mask menjadi gambar berwarna (BGR)
                    black_mask_bgr = cv2.cvtColor(black_mask, cv2.COLOR_GRAY2BGR)

                    # Ganti piksel putih dengan warna kuning
                    black_mask_bgr[np.where((black_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 0, 255]
                    cv2.imwrite('blackMaskBgr.png', black_mask_bgr)

                    black_pixels = cv2.countNonZero(black_mask)
                    print(f'Jumlah piksel minyak di dalam daun: {black_pixels}')

                    if (black_pixels > 50):
                        print("Kualitas daun Berminyak")
                    else:
                        print("Kualitas daun Berminyak")

                    # Ubah gambar grayscale menjadi BGR
                    segmented_image_bgrblack = cv2.cvtColor(segmented_image_gray, cv2.COLOR_GRAY2BGR)

                    # Gabungkan gambar BGR dengan mask kuning
                    combined_imageblack = cv2.addWeighted(segmented_image_bgrblack, 0.7, black_mask_bgr, 0.3, 0)

                    # Simpan gambar hasil gabungan
                    cv2.imwrite('combined_output_oil.png', combined_imageblack)

                    # Hitung jumlah piksel untuk setiap nilai intensitas dari 0 hingga 255
                    pixel_counts = np.bincount(segmented_image_gray.flatten(), minlength=256)

                    # Tentukan rentang warna dari 1 hingga 255
                    lower_range = np.array([1], dtype=np.uint8)
                    upper_range = np.array([255], dtype=np.uint8)

                    # Buat mask untuk rentang warna
                    range_mask = cv2.inRange(segmented_image_gray, lower_range, upper_range)

                    # Hitung jumlah piksel dalam rentang 1 hingga 255
                    range_pixels = cv2.countNonZero(range_mask)
                    print(f'Jumlah piksel dalam rentang 1 hingga 255: {range_pixels}')

                    # Hitung persentase
                    percentageOil = (black_pixels / range_pixels) * 100

                    # Cetak hasil
                    print(f'Persentase piksel minyak di dalam daun: {percentageOil:.2f}%')

                    # Hitung persentase
                    percentageKerusakan = (white_pixels / range_pixels) * 100

                    # Cetak hasil
                    print(f'Persentase kerusakan di dalam daun: {percentageKerusakan:.2f}%')

                    # Cetak jumlah piksel untuk setiap nilai intensitas dari 1 hingga 255
                    for intensity in range(1, 256):
                        print(f'Jumlah piksel dengan intensitas {intensity}: {pixel_counts[intensity]}')

                    else:
                        print("Tidak ada objek yang terdeteksi. Gambar mungkin terlalu gelap atau terang.")
                        segmented_image = None

            self.label_dimensions.config(
                text=f"Panjang daun: {panjang:.2f} cm\nPanjang : {PixelPanjang} px\nLebar daun: {lebar:.2f} cm\nLebar : {PixelLebar} px\nKualitas daun: {kualitas}\nBanyak Minyak :  {percentageOil:.2f}%\nKerusakan :  {percentageKerusakan:.2f}%\nWarna  :  {dominant_value}\nFrekwensizxx  :  {dominant_frequency}"
            )
        else:
            print("Path gambar tidak ditemukan.")

    def determine_leaf_quality(self, panjang):
        if panjang > 45:
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
