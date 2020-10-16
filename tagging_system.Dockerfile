FROM ubuntu:18.04

LABEL maintainer="alexanderbaranof@gmail.com"

# Настройки для сборки Ubuntu
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем зависимости
RUN apt update
RUN apt install -y git
RUN apt install -y p7zip-full
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y python3-opencv
RUN apt install -y tesseract-ocr
RUN apt install -y imagemagick
RUN apt install -y xpdf
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off
RUN apt install -y htop
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install pytesseract
RUN pip3 install pdfplumber
RUN pip3 install tqdm
RUN pip3 install python-docx
RUN pip3 install flask
RUN pip3 install torch==1.4.0+cpu torchvision==0.5.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install cython
RUN pip3 install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN pip3 install pycocotools
RUN pip3 install detectron2==0.1.1 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/index.html
RUN pip3 install openpyxl
RUN pip3 install gevent

# Задаем рабочую папку
WORKDIR /home/flask_app/

# Копируем данные для OCR

COPY ./tesseract_data/. /usr/share/tesseract-ocr/4.00/tessdata/

# Копируем все содержание текущего каталога в рабочую папку
COPY . .

# Команда при запуске
RUN chmod +x /home/flask_app/run_system.sh
CMD ["/home/flask_app/run_system.sh"]

# Открываем порты
EXPOSE 5000