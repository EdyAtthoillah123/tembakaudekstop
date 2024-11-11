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


    def process_image(self, path, contrast_factor=1.0):
        if os.path.exists(path):
            # Read the image from the provided path using OpenCV
            image = cv2.imread(path)

            if image is None:
                print("Image not found at path:", path)
                return

            # Save the original image
            cv2.imwrite("Original_Image.png", image)
            print("Image successfully read and saved as 'Original_Image.png'.")

            # Adjust contrast
            adjusted_image = self.adjust_contrast(image, contrast_factor)

            # Save the contrast-adjusted image
            cv2.imwrite("Adjusted_Contrast_Image.png", adjusted_image)
            print("Contrast-adjusted image saved as 'Adjusted_Contrast_Image.png'.")

            # Convert image to Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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
                cv2.imwrite('2 Image Segmented.png', segmented_image)

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
                cv2.imwrite('3 result_with_inner_contour.png', result_with_inner_contour)

                if len(segmented_image.shape) == 3:
                    # Konversi citra berwarna (3 channel) menjadi grayscale
                    segmented_image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('4 segmented_image_gray.png', segmented_image_gray)
                    # Menggunakan Gaussian Blur sebelum deteksi tepi

                    inner_segmented_gray = cv2.cvtColor(result_with_inner_contour, cv2.COLOR_RGBA2GRAY)
                    cv2.imwrite('5 Inner_Segmented_Gray.png', inner_segmented_gray)

                                # Calculate GLCM features and classify texture
                    glcm_features = self.calculate_glcm(segmented_image_gray)
                    texture = self.classify_texture(glcm_features)
                    print(f"Leaf texture: {texture}")
                    
                    # Tentukan rentang warna hitam (minyak)
                    lower_black = np.array([1], dtype=np.uint8)
                    upper_black = np.array([32], dtype=np.uint8)

                    # Buat mask untuk warna hitam
                    black_mask = cv2.inRange(inner_segmented_gray, lower_black, upper_black)
                    
                    # Deteksi tepi dengan Canny untuk menemukan tulang daun
                    edges = cv2.Canny(inner_segmented_gray, 50, 150)
                    cv2.imwrite('6 edges.png', edges)

                    # Dilatasi untuk mempertebal tepi tulang daun
                    kernel = np.ones((1, 3), np.uint8)
                    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
                    cv2.imwrite('7 dilated_edges.png', dilated_edges)

                    # Buat mask tulang daun
                    leaf_veins_mask = cv2.bitwise_not(dilated_edges)
                    cv2.imwrite('8 leaf_veins_mask.png', leaf_veins_mask)

                    # Terapkan leaf_veins_mask pada black_mask agar tulang daun tidak ikut terdeteksi sebagai minyak
                    filtered_black_mask = cv2.bitwise_and(black_mask, black_mask, mask=leaf_veins_mask)
                    black_pixels_filtered = cv2.countNonZero(filtered_black_mask)

                    # Ganti piksel hitam (minyak) dengan warna kuning pada gambar BGR
                    filtered_black_mask_bgr = cv2.cvtColor(filtered_black_mask, cv2.COLOR_GRAY2BGR)
                    filtered_black_mask_bgr[np.where((filtered_black_mask_bgr == [255, 255, 255]).all(axis=2))] = [0, 255, 255]
                    cv2.imwrite('9 filtered_blackMaskBgr.png', filtered_black_mask_bgr)

                    print("Jumlah piksel hitam setelah filter tulang daun:", black_pixels_filtered)

                    PanjangDaun = max(panjang, 0)
                    # Mengirim data ke Arduino
                    # Kategori warna berdasarkan average_hue dan average_value

                    # Format string yang ingin dikirim
                    grading = f"{kualitas}" 
                    self.send_hue_and_color_category(kualitas, grading)                    
                    self.label_dimensions.config(
                        text=f"Grade:\n {kualitas} \nPanjang Asli: {panjang:.1f}\nPanjang: {pixel_panjang}\nLebar: {pixel_lebar}\nPixel: {black_pixels_filtered}\nEntropy: {glcm_features[4]:.2f}\nTekstur: {texture}"
                    )

                else: 
                    print("Segmented Not Found")
            else:
                print("Contour Not Found")
        else:
            print("Image path not found.")

    
    def adjust_contrast(self, image, factor):
        # Mengonversi gambar ke format float32 agar tidak terjadi overflow
        adjusted = cv2.convertScaleAbs(image, alpha=factor, beta=0)
        return adjusted

    def calculate_glcm(self, image):
        # Calculate GLCM features using Haralick method and take the mean across different directions
        glcm = mahotas.features.haralick(image).mean(axis=0)
        return glcm

    def classify_texture(self, glcm_features):
        # Print all GLCM feature values for debugging
        print("GLCM Feature Values:", glcm_features)
        
        # Classification thresholds based on Entropy (glcm_features[4])
        if glcm_features[4] <= 0.45:
            texture = "Halus"  # Smooth texture
        elif 0.45 < glcm_features[4] <= 0.475:
            texture = "Sedang"  # Moderate texture
        else:
            texture = "Kasar"  # Rough texture

        # Print the selected feature (Entropy) and the classification result
        print(f"Entropy: {glcm_features[4]}, Classified as: {texture}")
        return texture


        # Print the selected feature (Entropy) and the classification result
        print(f"Entropy: {glcm_features[4]}, Classified as: {texture}")
        return texture


    def send_hue_and_color_category(self, oil, color_category):
        data = f"{oil},{color_category}\n"
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