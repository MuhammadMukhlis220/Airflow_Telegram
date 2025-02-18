---
# **Integrating Airflow Notification With Telegram**

*The DAG code provided in AIrflow staging's ip of Onyx Big Data Platform named kirim_telegram_notif*

Di repository ini kita akan belajar untuk mengintegrasikan airflow mengirim notifikasi perihal DAG ke user menggunakan aplikasi Telegram.

## Step 1 Daftar Bot
Di telegram cari pengguna dengan mencari username BotFather
Kemudian gunakan command di gambar berikut untuk berinteraksi dengan BotFather dengan tujuan membuat bot.

![Alt Text](/pic/register_1.png)
Gambar 1

**Perlu diingat bahwa command yang diberikan bisa-bisa berubah setiap waktu.**

Catat API token yang diberikan seperti yang dikotaki berwarna merah. Jika token tidak ada coba untuk bertanya ke BotFather lagi tentang bot yang kita buat seperti gambah di bawah ini:

![Alt Text](/pic/register_2.png)

Gambar 2

Setelah mendapatkan token, pergi ke url : `https://api.telegram.org/bot<TOKEN_BOT_YANG_DIBUAT>/getUpdates`
Tujuannya adalah untuk mencari ID akun penerima notifikasi airflow.
Coba cari username bot anda dan chat apapun dengannya.

![Alt Text](/pic/register_3.png)

Gambar 3

Kemudian cek url dengan me-refresh web pagenya dan hasilnya kita akan mencatat ID akun yang berbicara dengan bot kita.

![Alt Text](/pic/register_4.png)

Gambar 4

Catat nomor ID seperti yang dikotaki berwarna merah.

**Sampai sini kita sudah mendapatkan akun bot dengan tokennya dan id penerima.**

## Step 2 Buat DAG Airflow

Kita akan menggunakan pemrograman python untuk membuat DAG-nya. Library yang dibutuhkan adalah telegram dengan versi 13.15. Gunakan: `pip install python-telegram-bot==13.15` untuk mengistall library-nya. Sisa library yang di-import adalah bawaan dari airflow dan pythonnya langsung.

For the complete Python programming code, refer to the following block.
<details>
   <summary>Click to view the complete Python code.</summary>

   ```python
import telegram # pip install python-telegram-bot==13.15
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pytz

TELEGRAM_BOT_TOKEN = "x:x" # bot punya mukhlis / pake aja, nanti ada bot namanya Bobyjhow yg kirim notif ke kalian
TELEGRAM_CHAT_ID = "x" # tujuan akun untuk dikirim notif / ini akun id mukhlis / please jangan spam ke sini @.@

def send_telegram_success_final_message(**context):
    
    #Mengirim notifikasi ke Telegram saat semua task selesai sukses
    dag_id = context["dag"].dag_id
    message = f"✅✅✅ All task in DAG: {dag_id} finish without error! 🎉🎉🎉"
    
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def send_telegram_fail_alert(context):
    task_instance = context.get('task_instance')
    dag_id = context.get('dag').dag_id
    task_id = task_instance.task_id
    execution_date = context.get('data_interval_start') # bentuknya UTC, nanti di-convert pake pytz
    exception = str(context.get('exception'))  # Konversi error ke string

    # convert UTC ke WIB / UTC + 7
    wib = pytz.timezone("Asia/Jakarta")
    execution_date_wib = execution_date.astimezone(wib).strftime("%Y-%m-%d %H:%M:%S %Z")
    
    message = (
        f"❌⚠️❌ Task Failed in Airflow! ❌⚠️❌\n"
        f"DAG: {dag_id}\n"
        f"Task: {task_id}\n"
        f"Execution Date: {execution_date_wib}\n"
        f"Error: {exception}"
    )

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

default_args = {
    'owner': 'mukhlis',
    'start_date': datetime(2025, 2, 10),
    #"on_success_callback": send_telegram_success_message, untuk mengirim notifikasi SETIAP TASK yang berhasil
    'on_failure_callback': send_telegram_fail_alert
}

dag = DAG(
    'kirim_telegram_notif',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    tags=['test', 'telegram', 'python']
)

# Task yang akan gagal
def task_gagal():
    print("halo-halo bandung")
    #raise ValueError('Task ini gagal! Disengaja')

t1 = PythonOperator(
    task_id='task_gagal',
    python_callable=task_gagal,
    #on_success_callback=send_telegram_success_final_message untuk mengirim notifikasi SAAT TASK t1 selesai
    dag=dag
)

success_message = PythonOperator(
    task_id="kirim_notif_sukses",
    python_callable=send_telegram_success_final_message,
    provide_context=True,  # Wajib agar fungsi bisa menerima `context`
    dag=dag,
)

t1 >> success_message


   ```
   </details>


Untuk membuat code kita mengirim notifikasi, airflow sudah memberikan kita ruang untuk berkreasi di dalam parameter `default_args`. Di dalam `default_args` terdapat dua parameter yang tujuannya adalah "Jika task gagal akan eksekusi apa? dan jika task berhasil akan eksekusi apa?" kedua itu ada di dalam parameter `on_failure_callback` dan `on_success_callback`. 

Jika kita ingin airflow melakukan sesuatu saat **setiap task** gagal atau berhasil, maka kita harus mengisi kedua parameter tersebut. DI case kali ini **kita akan mengirim notifikasi jika satu task gagal dan mengirim notifikasi jika semua task berhasil**. Karena kita akan mengirim notifikasi jika task gagal maka kita akan mengisi parameter `on_failure_callback` **tanpa** mengisi parameter `on_success_callback`. Jika kita mengisi parameter `on_success_callback` yang terjadi adalah ada perlakukan airflow di setiap task yang berhasil, dimana kita ingin perlakuannya dieksekusi ketika **semua task** berhasil.

Mari kita masukkan library yang dibutuhkan dan variabel untuk token dan id akun.

![Alt Text](/pic/code_0.png)

Gambar 5

Kita membuat fungsi `send_telegram_fail_alert(context)` yang akan diisi untuk parameter `on_failure_callback`. Isi dari pesan ini adalah variabel-variabel dari fungsi DAG yang sudah disediakan secara default oleh airflow seperti anma dag, dama task dan eaktu eksekusi dengan memanggil `context`. Kita menggunakan pytz untuk mengubah waktu yang tidak sesuai menjadi time zone yang kita inginkan.

![Alt Text](/pic/code_2.png)

Gambar 6

Untuk mengirim notifikasi yang berisi DAG berhasil dijalankan tanpa error, kita membuat fungsi kedua bernama `send_telegram_success_final_message(**context)`.

![Alt Text](/pic/code_3.png)

Gambar 7

Fungsi tersebut kita jadikan sebagai task terakhir yang akan dieksekusi

![Alt Text](/pic/code_4.png)

Gambar 8

## Step 3 Cek Hasil

Ketika task gagal maka akan ada notifikasi ke id pengguna yang kita daftarkan di variabel `TELEGRAM_CHAT_ID`. Hasilnya adalah:

![Alt Text](/pic/result_1.png)

Gambar 9

Ketika DAG berhasil dijalankan, kita mengeksekusi task terakhir yaitu mengirim notifikasi berhasil:

![Alt Text](/pic/result_2.png)

Gambar 10
