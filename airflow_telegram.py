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