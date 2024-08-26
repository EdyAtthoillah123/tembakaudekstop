import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import rgb2gray
import matplotlib.image as mpimg


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
            file_path = os.path.join(directory, "captured_image.jpg")
            self.current_image.save(file_path)
            
            # Process the saved image
            self.process_image(file_path)
        else:
            print("No image to save!")

    def process_image(self, path):
        if os.path.exists(path):
            image = mpimg.imread(path)
            
            # Konversi Image Ke Grayscale
            img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

            # Segmentasi Citra Menggunakan Thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
            
            # Temukan Kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Asumsikan kita hanya ingin kontur terbesar
            largest_contour = max(contours, key=cv2.contourArea)

            # Buat bounding box di sekitar kontur terbesar
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Crop gambar berdasarkan bounding box
            cropped_image = image[y:y+h, x:x+w]
            
            # Buat mask kosong
            mask = np.zeros_like(img_gray)
            
            # Isi area kontur pada mask dengan warna putih (255)
            cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
            
            # Segmentasi objek dengan mask
            segmented_image = cv2.bitwise_and(image, image, mask=mask)
            
            # Konversi Image Ke Grayscale
            gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
            
            # Deteksi Tepi Menggunakan Canny
            edges = cv2.Canny(gray_segmented_image, 100, 200)

            # plt.imshow(edges)
            # plt.title('Image ')
            # plt.axis('off')
            # plt.show()
            
            # Analisis Mutu dengan Edge Detection
            num_edges = np.count_nonzero(edges)
            
            threshold_value = 4700
            # Menentukan Mutu Berdasarkan Jumlah Tepi
            quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
            image = cv2.imread(path)
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Segment the image using thresholding
            _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Calculate dimensions
                panjang = 0.0935 * w - 8.0649
                lebar = 0.0151 * h - 0.0715
                PixelPanjang = w
                PixelLebar = h

                kualitas_daun = self.determine_leaf_quality(panjang)

                cropped_image = image[y:y+h, x:x+w]

                # plt.imshow(cropped_image)
                # plt.title('Image ')
                # plt.axis('off')
                # plt.show()

                # Create an empty mask
                mask = np.zeros_like(img_gray)
                
                # Fill the contour area on the mask
                cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
                
                segmented_image = cv2.bitwise_and(image, image, mask=mask)
                # plt.imshow(segmented_image)
                # plt.title('Image ')
                # plt.axis('off')
                # plt.show()
                gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
                
                edges = cv2.Canny(gray_segmented_image, 100, 200)
                num_edges = np.count_nonzero(edges)
                
                threshold_value = 4700
            quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
            
            self.label_dimensions.config(
                text=f"Panjang daun: {panjang:.2f} cm\nPanjang : {PixelPanjang} px\nLebar daun: {lebar:.2f} cm\nLebar : {PixelLebar} px\nKualitas daun: {kualitas_daun}\nKualitas Daun: \n{quality}"
            )
            
            print(quality)
        else:
            print("Tidak ada objek yang terdeteksi. Gambar mungkin terlalu gelap atau terang.")
            pass

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


# ini
# class WebcamApp:
#     def __init__(self, window):
#         self.window = window
#         self.window.title("Webcam App")

#         # Initialize video capture
#         self.video_capture = cv2.VideoCapture(0)

#         # Styling configuration
#         self.window.configure(bg="#2c3e50")
#         self.window.geometry("960x600")

#         # Grid configuration for responsiveness
#         self.window.grid_columnconfigure(0, weight=1)
#         self.window.grid_columnconfigure(1, weight=1)
#         self.window.grid_rowconfigure(0, weight=1)
#         self.window.grid_rowconfigure(1, weight=1)

#         # Webcam display with border and shadow effect
#         self.frame_webcam = tk.Frame(window, bg="#2c3e50", bd=2, relief=tk.RAISED)
#         self.frame_webcam.grid(row=0, column=0, padx=20, pady=20)

#         self.canvas_webcam = tk.Canvas(
#             self.frame_webcam, width=640, height=480, bg="#34495e", bd=0, highlightthickness=0
#         )
#         self.canvas_webcam.pack()

#         # Modern label with rounded corners
#         self.label_frame = tk.Frame(window, bg="#34495e", bd=5, relief=tk.FLAT)
#         self.label_frame.grid(row=0, column=1, sticky=tk.NW, padx=20, pady=20)

#         self.label_dimensions = tk.Label(
#             self.label_frame, text="", font=("Arial", 14, "bold"), fg="#ecf0f1", bg="#34495e", padx=10, pady=10
#         )
#         self.label_dimensions.pack(anchor=tk.NW)

#         # Capture Button with modern style and icon
#         self.button_capture = tk.Button(
#             window, text="Capture", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c",
#             activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
#             command=self.download_image
#         )
#         self.button_capture.grid(row=1, column=0, pady=20, padx=20)

#         # Close Button with hover effect
#         self.button_close = tk.Button(
#             window, text="Close", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c",
#             activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
#             command=window.quit
#         )
#         self.button_close.grid(row=1, column=1, pady=20, padx=20)

#         self.button_close.bind("<Enter>", self.on_enter)
#         self.button_close.bind("<Leave>", self.on_leave)

#         # Start video loop
#         self.update_frame()

#     def update_frame(self):
#         ret, frame = self.video_capture.read()
#         if ret:
#             self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
#             self.canvas_webcam.create_image(0, 0, image=self.photo, anchor=tk.NW)
#         self.window.after(10, self.update_frame)

#     def on_closing(self):
#         self.video_capture.release()
#         self.window.destroy()

#     def on_enter(self, e):
#         e.widget['bg'] = '#d35400'

#     def on_leave(self, e):
#         e.widget['bg'] = '#e74c3c'

#     def update_webcam(self):
#         ret, frame = self.video_capture.read()
#         if ret:
#             gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
#             # Deteksi kontur untuk memeriksa keberadaan objek
#             _, thresh = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY_INV)
#             contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
#             if contours:
#                 # Temukan kontur terbesar (anggap sebagai objek daun)
#                 largest_contour = max(contours, key=cv2.contourArea)
#                 x, y, w, h = cv2.boundingRect(largest_contour)
                
#                 # Gambar kotak pembatas di sekitar objek
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
#                 # Proses gambar secara otomatis jika objek terdeteksi
#                 self.process_frame(frame)
            
#             # Tampilkan gambar di antarmuka Tkinter dengan kotak pembatas
#             self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#             self.photo_webcam = ImageTk.PhotoImage(image=self.current_image)
#             self.canvas_webcam.create_image(0, 0, image=self.photo_webcam, anchor=tk.NW)
            
#             # Perbarui frame setiap 15 milidetik
#             self.window.after(50, self.update_webcam)


#     def process_frame(self, frame):
#         # Simpan gambar yang terdeteksi untuk diproses
#         directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#         file_path = os.path.join(directory, "captured_image.jpg")
#         Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(file_path)
        
#         # Proses gambar yang tersimpan
#         self.process_image(file_path)


#     def download_image(self):
#         if self.current_image is not None:
#             directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
#             if not os.path.exists(directory):
#                 os.makedirs(directory)
#             file_path = os.path.join(directory, "captured_image.jpg")
#             self.current_image.save(file_path)
#             # os.startfile(file_path) ``
            
#             # Automatically process the image after saving
#             self.process_image(file_path)
    
#     def determine_leaf_quality(self, panjang):
#         if panjang > 45:
#             return "Super"
#         elif 40 <= panjang <= 45:
#             return "Lente 1"
#         elif 35 <= panjang < 40:
#             return "Lente 2"
#         elif 30 <= panjang < 35:
#             return "Lente 3"
#         else:
#             return "Filler"

#     def process_image(self, path):
#         if os.path.exists(path):
#             # Load the captured image
#             image = cv2.imread(path)
#             hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#             lower_green = np.array([35, 40, 40])  # Rentang bawah warna hijau
#             upper_green = np.array([85, 255, 255])  # Rentang atas warna hijau
#             mask = cv2.inRange(hsv, lower_green, upper_green)
#             result = cv2.bitwise_and(image, image, mask=mask)
#             green_area = cv2.countNonZero(mask)
#             total_area = mask.shape[0] * mask.shape[1]
#             proportion = green_area / total_area

#             print(f"Proportion of green area: {proportion:.2%}")
#             img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
#             # Segmentasi Citra Menggunakan Thresholding
#             _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
#             contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             if contours:  # Pastikan ada kontur yang ditemukan
#                 # Temukan kontur terbesar (anggap sebagai objek daun)
#                 largest_contour = max(contours, key=cv2.contourArea)
#                 x, y, w, h = cv2.boundingRect(largest_contour)
                
#                 # Calculate dimensions
#                 panjang = 0.0154 * w - 0.165
#                 lebar = 0.0151 * h - 0.0715

#                 PixelPanjang = w
#                 PixelLebar = h

#                 # Determine leaf quality
#                 kualitas_daun = self.determine_leaf_quality(panjang)

#                 # Crop gambar berdasarkan bounding box
#                 cropped_image = image[y:y+h, x:x+w]

#                 # Buat mask kosong
#                 mask = np.zeros_like(img_gray)
                
#                 # Isi area kontur pada mask dengan warna putih (255)
#                 cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
                
#                 # Segmentasi objek dengan mask
#                 segmented_image = cv2.bitwise_and(image, image, mask=mask)
                
#                 # Konversi Image Ke Grayscale
#                 gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
                
#                 # Deteksi Tepi Menggunakan Canny
#                 edges = cv2.Canny(gray_segmented_image, 100, 200)
#                 # Analisis Mutu dengan Edge Detection
#                 num_edges = np.count_nonzero(edges)
                
#                 threshold_value = 4700
#                 # Menentukan Mutu Berdasarkan Jumlah Tepi
#                 quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
                
#                 self.label_dimensions.config(
#                     text=f"Panjang daun: {panjang:.2f} cm\nPanjang : {PixelPanjang} px\nLebar daun: {lebar:.2f} cm\nLebar : {PixelLebar} px\nKualitas daun: {kualitas_daun}\nKualitas Daun: \n{quality}"
#                 )
                
#                 print(quality)
#             else:
#                 print("Tidak ada objek yang terdeteksi. Gambar mungkin terlalu gelap atau terang.")


# root = tk.Tk()
# app = WebcamApp(root)
# root.protocol("WM_DELETE_WINDOW", app.on_closing)
# root.mainloop()


# class WebcamApp:
#     def __init__(self, window):
#         self.window = window
#         self.window.title("Webcam App")

#         # Initialize video capture
#         self.video_capture = cv2.VideoCapture(0)

#         # Styling configuration
#         self.window.configure(bg="#2c3e50")
#         self.window.geometry("960x600")
        
#         # Webcam display
#         self.canvas_webcam = tk.Canvas(window, width=640, height=480, bg="#34495e", bd=0, highlightthickness=0)
#         self.canvas_webcam.grid(row=0, column=0, padx=20, pady=20)
        
#         # Label for leaf dimensions and quality
#         self.label_dimensions = tk.Label(
#             window, text="", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50", justify=tk.LEFT
#         )
#         self.label_dimensions.grid(row=0, column=1, sticky=tk.NW, padx=20, pady=20)
#         self.update_webcam()

# class WebcamApp:
#     def __init__(self, window):
#         self.window = window
#         self.window.title("Webcam App")

#         # Initialize video capture
#         self.video_capture = cv2.VideoCapture(0)

#         # Styling configuration
#         self.window.configure(bg="#2c3e50")
#         self.window.geometry("960x600")
        
#         # Webcam display with border and shadow effect
#         self.frame_webcam = tk.Frame(window, bg="#2c3e50", bd=2, relief=tk.RAISED)
#         self.frame_webcam.grid(row=0, column=0, padx=20, pady=20)
        
#         self.canvas_webcam = tk.Canvas(
#             self.frame_webcam, width=640, height=480, bg="#34495e", bd=0, highlightthickness=0
#         )
#         self.canvas_webcam.pack()

#         # Modern label with rounded corners
#         self.label_frame = tk.Frame(window, bg="#34495e", bd=5, relief=tk.FLAT)
#         self.label_frame.grid(row=0, column=1, sticky=tk.NW, padx=20, pady=20)
        
#         self.label_dimensions = tk.Label(
#             self.label_frame, text="", font=("Arial", 14, "bold"), fg="#ecf0f1", bg="#34495e", padx=10, pady=10
#         )
#         self.label_dimensions.pack(anchor=tk.NW)

#         # Capture Button with modern style
#         self.button_capture = tk.Button(
#             window, text="Capture", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c", 
#             activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10
#         )
#         self.button_capture.grid(row=1, column=0, pady=20, padx=20)

#         # Close Button
#         self.button_close = tk.Button(
#             window, text="Close", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#e74c3c", 
#             activebackground="#c0392b", activeforeground="#ecf0f1", bd=0, padx=20, pady=10,
#             command=window.quit
#         )
#         self.button_close.grid(row=1, column=1, pady=20, padx=20)

#         # Start video loop
#         self.update_frame()

#     def update_frame(self):
#         ret, frame = self.video_capture.read()
#         if ret:
#             self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
#             self.canvas_webcam.create_image(0, 0, image=self.photo, anchor=tk.NW)
#         self.window.after(10, self.update_frame)

#     def on_closing(self):
#         self.video_capture.release()
#         self.window.destroy()

#     def update_webcam(self):
#             ret, frame = self.video_capture.read()
#             if ret:
#                 gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
#                 # Deteksi kontur untuk memeriksa keberadaan objek
#                 _, thresh = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY_INV)
#                 contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
#                 if contours:
#                     # Temukan kontur terbesar (anggap sebagai objek daun)
#                     largest_contour = max(contours, key=cv2.contourArea)
#                     x, y, w, h = cv2.boundingRect(largest_contour)
                    
#                     # Gambar kotak pembatas di sekitar objek
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
#                     # Proses gambar secara otomatis jika objek terdeteksi
#                     self.process_frame(frame)
                
#                 # Tampilkan gambar di antarmuka Tkinter dengan kotak pembatas
#                 self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#                 self.photo_webcam = ImageTk.PhotoImage(image=self.current_image)
#                 self.canvas_webcam.create_image(0, 0, image=self.photo_webcam, anchor=tk.NW)
                
#                 # Perbarui frame setiap 15 milidetik
#                 self.window.after(50, self.update_webcam)


#     def process_frame(self, frame):
#         # Simpan gambar yang terdeteksi untuk diproses
#         directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#         file_path = os.path.join(directory, "captured_image.jpg")
#         Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(file_path)
        
#         # Proses gambar yang tersimpan
#         self.process_image(file_path)


#     def download_image(self):
#         if self.current_image is not None:
#             directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
#             if not os.path.exists(directory):
#                 os.makedirs(directory)
#             file_path = os.path.join(directory, "captured_image.jpg")
#             self.current_image.save(file_path)
#             # os.startfile(file_path) ``
            
#             # Automatically process the image after saving
#             self.process_image(file_path)
    
#     def determine_leaf_quality(self, panjang):
#         if panjang > 45:
#             return "Super"
#         elif 40 <= panjang <= 45:
#             return "Lente 1"
#         elif 35 <= panjang < 40:
#             return "Lente 2"
#         elif 30 <= panjang < 35:
#             return "Lente 3"
#         else:
#             return "Filler"

#     def process_image(self, path):
#         if os.path.exists(path):
#             # Load the captured image
#             image = cv2.imread(path)
#             hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#             lower_green = np.array([35, 40, 40])  # Rentang bawah warna hijau
#             upper_green = np.array([85, 255, 255])  # Rentang atas warna hijau
#             mask = cv2.inRange(hsv, lower_green, upper_green)
#             result = cv2.bitwise_and(image, image, mask=mask)
#             green_area = cv2.countNonZero(mask)
#             total_area = mask.shape[0] * mask.shape[1]
#             proportion = green_area / total_area

#             print(f"Proportion of green area: {proportion:.2%}")
#             img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
#             # Segmentasi Citra Menggunakan Thresholding
#             _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
#             contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             if contours:  # Pastikan ada kontur yang ditemukan
#                 # Temukan kontur terbesar (anggap sebagai objek daun)
#                 largest_contour = max(contours, key=cv2.contourArea)
#                 x, y, w, h = cv2.boundingRect(largest_contour)
                
#                 # Calculate dimensions
#                 panjang = 0.0154 * w - 0.165
#                 lebar = 0.0151 * h - 0.0715

#                 PixelPanjang = w
#                 PixelLebar = h

#                 # Determine leaf quality
#                 kualitas_daun = self.determine_leaf_quality(panjang)

#                 # Crop gambar berdasarkan bounding box
#                 cropped_image = image[y:y+h, x:x+w]

#                 # Buat mask kosong
#                 mask = np.zeros_like(img_gray)
                
#                 # Isi area kontur pada mask dengan warna putih (255)
#                 cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
                
#                 # Segmentasi objek dengan mask
#                 segmented_image = cv2.bitwise_and(image, image, mask=mask)
                
#                 # Konversi Image Ke Grayscale
#                 gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
                
#                 # Deteksi Tepi Menggunakan Canny
#                 edges = cv2.Canny(gray_segmented_image, 100, 200)
#                 # Analisis Mutu dengan Edge Detection
#                 num_edges = np.count_nonzero(edges)
                
#                 threshold_value = 4700
#                 # Menentukan Mutu Berdasarkan Jumlah Tepi
#                 quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
                
#                 self.label_dimensions.config(
#                     text=f"Panjang daun: {panjang:.2f} cm\nPanjang : {PixelPanjang} px\nLebar daun: {lebar:.2f} cm\nLebar : {PixelLebar} px\nKualitas daun: {kualitas_daun}\nKualitas Daun: \n{quality}"
#                 )
                
#                 print(quality)
#             else:
#                 print("Tidak ada objek yang terdeteksi. Gambar mungkin terlalu gelap atau terang.")

# root = tk.Tk()
# app = WebcamApp(root)

# root.mainloop()

    # def update_webcam(self):
    #     ret, frame = self.video_capture.read()
    #     if ret:
    #         self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    #         self.photo_webcam = ImageTk.PhotoImage(image=self.current_image)
    #         self.canvas_webcam.create_image(0, 0, image=self.photo_webcam, anchor=tk.NW)
    #         self.window.after(15, self.update_webcam)

    # def update_webcam(self):
    #     ret, frame = self.video_capture.read()
    #     if ret:
    #         self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    #         self.photo_webcam = ImageTk.PhotoImage(image=self.current_image)
    #         self.canvas_webcam.create_image(0, 0, image=self.photo_webcam, anchor=tk.NW)
            
    #         # Convert frame to grayscale for processing
    #         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
    #         # Detect contours to check for leaf presence
    #         _, thresh = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY_INV)
    #         contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
    #         if contours:
    #             # Automatically process the image if a leaf is detected
    #             self.process_frame(frame)

    #         self.window.after(15, self.update_webcam)

    # def process_image(self, path):
    #     if os.path.exists(path):
    #         # Load the captured image
    #         image = cv2.imread(path)
    #         img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
    #         # Segmentasi Citra Menggunakan Thresholding
    #         _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
    #         contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #         largest_contour = max(contours, key=cv2.contourArea)
    #         x, y, w, h = cv2.boundingRect(largest_contour)
            
    #         # Calculate dimensions
    #         panjang = 0.0154 * w - 0.165
    #         lebar = 0.0151 * h - 0.0715

    #         PixelPanjang = w
    #         PixelLebar = h

    #         # Determine leaf quality
    #         kualitas_daun = self.determine_leaf_quality(panjang)
            

    #         # Crop gambar berdasarkan bounding box
    #         cropped_image = image[y:y+h, x:x+w]

    #         # Buat mask kosong
    #         mask = np.zeros_like(img_gray)
            
    #         # Isi area kontur pada mask dengan warna putih (255)
    #         cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
            
    #         # Segmentasi objek dengan mask
    #         segmented_image = cv2.bitwise_and(image, image, mask=mask)
            
    #         # Konversi Image Ke Grayscale
    #         gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
            
    #         # Deteksi Tepi Menggunakan Canny
    #         edges = cv2.Canny(gray_segmented_image, 100, 200)
    #         # Analisis Mutu dengan Edge Detection
    #         num_edges = np.count_nonzero(edges)
            
    #         threshold_value = 4700
    #         # Menentukan Mutu Berdasarkan Jumlah Tepi
    #         quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
            
    #         self.label_dimensions.config(
    #             text=f"Panjang daun: {panjang:.2f} cm\nPanjang : {PixelPanjang} px\nLebar daun: {lebar:.2f} cm\nLebar : {PixelLebar} px\nKualitas daun: {kualitas_daun}\nKualitas Daun: \n{quality}"
    #         )

    #         print(quality)




    # manual

    
# class WebcamApp:
#     def __init__(self, window):
#         self.window = window
#         self.window.title("Webcam App")

#         # Initialize video capture
#         self.video_capture = cv2.VideoCapture(0)

#         # Styling configuration
#         self.window.configure(bg="#2c3e50")
#         self.window.geometry("960x600")
        
#         # Webcam display
#         self.canvas_webcam = tk.Canvas(window, width=640, height=480, bg="#34495e", bd=0, highlightthickness=0)
#         self.canvas_webcam.grid(row=0, column=0, padx=20, pady=20)
        
#         # Label for leaf dimensions and quality
#         self.label_dimensions = tk.Label(
#             window, text="", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50", justify=tk.LEFT
#         )
#         self.label_dimensions.grid(row=0, column=1, sticky=tk.NW, padx=20, pady=20)

#         # Capture & Process button
#         self.download_button = tk.Button(
#             window, text="Capture & Process", font=("Arial", 14, "bold"), fg="#ffffff", bg="#e74c3c",
#             activebackground="#c0392b", bd=0, padx=10, pady=10, command=self.capture_and_process
#         )
#         self.download_button.grid(row=2, column=0, columnspan=2, pady=20)

#         self.update_webcam_display()

#     def update_webcam_display(self):
#         ret, frame = self.video_capture.read()
#         if ret:
#             # Convert the frame to RGB for displaying
#             self.current_frame = frame
#             self.display_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#             self.photo_webcam = ImageTk.PhotoImage(image=self.display_frame)
#             self.canvas_webcam.create_image(0, 0, image=self.photo_webcam, anchor=tk.NW)

#         # Update the display every 15 milliseconds
#         self.window.after(15, self.update_webcam_display)

#     def capture_and_process(self):
#         if self.current_frame is not None:
#             # Process the current frame
#             self.process_frame(self.current_frame)

#     def process_frame(self, frame):
#         # Save the captured frame for processing
#         directory = os.path.expanduser("~/Documents/KlasifikasiTembakau")
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#         file_path = os.path.join(directory, "captured_image.jpg")
#         Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(file_path)
        
#         # Process the saved image
#         self.process_image(file_path)

#     def determine_leaf_quality(self, panjang):
#         if panjang > 45:
#             return "Super"
#         elif 40 <= panjang <= 45:
#             return "Lente 1"
#         elif 35 <= panjang < 40:
#             return "Lente 2"
#         elif 30 <= panjang < 35:
#             return "Lente 3"
#         else:
#             return "Filler"

#     def process_image(self, path):
#         if os.path.exists(path):
#             # Load image
#             image = mpimg.imread(path)
            
            
#             # Konversi Image Ke Grayscale
#             img_gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

#             # Segmentasi Citra Menggunakan Thresholding
#             _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
            
#             # Temukan Kontur
#             contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#             # Asumsikan kita hanya ingin kontur terbesar
#             largest_contour = max(contours, key=cv2.contourArea)

#             # Buat bounding box di sekitar kontur terbesar
#             x, y, w, h = cv2.boundingRect(largest_contour)
            
#             # Crop gambar berdasarkan bounding box
#             cropped_image = image[y:y+h, x:x+w]
            
#             # Buat mask kosong
#             mask = np.zeros_like(img_gray)
            
#             # Isi area kontur pada mask dengan warna putih (255)
#             cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
            
#             # Segmentasi objek dengan mask
#             segmented_image = cv2.bitwise_and(image, image, mask=mask)
            
#             # Konversi Image Ke Grayscale
#             gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
            
#             # Deteksi Tepi Menggunakan Canny
#             edges = cv2.Canny(gray_segmented_image, 100, 200)

#             plt.imshow(edges)
#             plt.title('Image ')
#             plt.axis('off')
#             plt.show()
            
#             # Analisis Mutu dengan Edge Detection
#             num_edges = np.count_nonzero(edges)
            
#             threshold_value = 4700
#             # Menentukan Mutu Berdasarkan Jumlah Tepi
#             quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
#             image = cv2.imread(path)
#             img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#             # Segment the image using thresholding
#             _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)
#             contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             if contours:
#                 largest_contour = max(contours, key=cv2.contourArea)
#                 x, y, w, h = cv2.boundingRect(largest_contour)
                
#                 # Calculate dimensions
#                 panjang = 0.0154 * w - 0.165
#                 lebar = 0.0151 * h - 0.0715
#                 PixelPanjang = w
#                 PixelLebar = h

#                 kualitas_daun = self.determine_leaf_quality(panjang)

#                 cropped_image = image[y:y+h, x:x+w]

#                 plt.imshow(cropped_image)
#                 plt.title('Image ')
#                 plt.axis('off')
#                 plt.show()

#                 # Create an empty mask
#                 mask = np.zeros_like(img_gray)
                
#                 # Fill the contour area on the mask
#                 cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
                
#                 segmented_image = cv2.bitwise_and(image, image, mask=mask)
#                 plt.imshow(segmented_image)
#                 plt.title('Image ')
#                 plt.axis('off')
#                 plt.show()
#                 gray_segmented_image = (255*rgb2gray(np.array(segmented_image))).astype(np.uint8)
                
#                 edges = cv2.Canny(gray_segmented_image, 100, 200)
#                 num_edges = np.count_nonzero(edges)
                
#                 threshold_value = 4700
#             quality = "Mutu Tinggi (Tidak Rusak)" if num_edges < threshold_value else "Mutu Rendah (Rusak)"
            
#             self.label_dimensions.config(
#                 text=f"Panjang daun: {panjang:.2f} cm\nPanjang : {PixelPanjang} px\nLebar daun: {lebar:.2f} cm\nLebar : {PixelLebar} px\nKualitas daun: {kualitas_daun}\nKualitas Daun: \n{quality}"
#             )
            
#             print(quality)
#         else:
#             print("Tidak ada objek yang terdeteksi. Gambar mungkin terlalu gelap atau terang.")

# root = tk.Tk()
# app = WebcamApp(root)
# root.mainloop()


