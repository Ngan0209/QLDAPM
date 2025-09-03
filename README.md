# QLDAPM

Ban đầu khi clone về thực hiện tạo thư mục .env và thêm các biến môi trường
CLOUDINARY_NAME="",
API_KEY="",
API_SECRET=""

DATABASE_URL=mysql+pymysql://root:%s@localhost/job_db?charset=utf8mb4
DATABASR_PASSWORD = ""
SECRET_KEY = HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG

sau đó thực hiện cài môi trường ảo và import các thư viện từ requirements.txt




sau đó thực hiện chạy file init db bằng lệnh
python -m app.__init_db

có thay đổi gì các trường của model thì thực hiện lệnh
flask db migrate -m "update models"
flask db upgrade
