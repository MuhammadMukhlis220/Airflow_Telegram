---
# **Integrating Airflow Notification With Telegram**

*The DAG code is already in the Airflow staging's IP of Onyx Big Data Platform, named `kirim_telegram_notif`.*

In this repository, we will learn how to integrate Airflow to send notifications about the DAG status to users via the Telegram application.

## Step 1 Register a Bot
Search for the user with the username `BotFather` on Telegram.
Then use the command shown in the image below to interact with BotFather in order to create a bot.

![Alt Text](/pic/register_1.png)
**Figure 1**

**Note**: The commands provided may change at any time.

Make sure to note the API token that is provided, as highlighted in red. If you do not receive the token, try asking BotFather again about the bot you created, as shown in the image below:

![Alt Text](/pic/register_2.png)
**Figure 2**

After obtaining the token, go to the following URL: `https://api.telegram.org/bot<TOKEN_OF_CREATED_BOT>/getUpdates`.
This URL will help you find the recipient account ID for Airflow notifications.
Try to search for your bot's username and send any message to it.

![Alt Text](/pic/register_3.png)
**Figure 3**

Then, refresh the page, and you will see the account ID of the user who is chatting with your bot.

![Alt Text](/pic/register_0.png)
**Figure 4**

Make sure to note down the account ID, as highlighted in red.

**At this point, you have obtained the bot's token and the recipient account's ID.**

## Step 2 Create Airflow DAG

We will use Python programming to create the DAG. The required library is `telegram` with version 13.15. Use: `pip install python-telegram-bot==13.15` to install the library. The remaining libraries are imported from Airflow and Python directly.

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

# Failed task
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


To make the code send notifications, Airflow provides us with space to be creative within the `default_args` parameter. Inside `default_args`, there are two parameters that determine "What should happen if a task fails? And what should happen if a task succeeds?" These two parameters are `on_failure_callback` and `on_success_callback`.

If we want Airflow to perform an action whenever **each task** fails or succeeds, we need to fill in both parameters. In this case, **we will send a notification if one task fails and send a notification if all tasks succeed**. Since we want to send a notification when a task fails, we will fill the `on_failure_callback` parameter **without** filling in the `on_success_callback`. If we filled in the `on_success_callback` parameter, what would happen is Airflow would apply the action for **every successful task**, whereas we want the action to be executed only when **all tasks** succeed.

Let’s add the necessary libraries and variables for the token and account ID.

![Alt Text](/pic/code_0.png)

**Figure 5**

We create the function `send_telegram_fail_alert(context)`, which will be assigned to the `on_failure_callback` parameter. The message will contain variables provided by Airflow’s default context, such as the DAG name, task name, and execution time, accessed using `context`. We use `pytz` to convert the time to the desired time zone.

![Alt Text](/pic/code_2.png)

**Figure 6**

To send a notification indicating that the DAG ran successfully without errors, we create a second function named `send_telegram_success_final_message(**context)`.

![Alt Text](/pic/code_3.png)

**Figure 7**

This function is set as the last task to be executed.

![Alt Text](/pic/code_4.png)

**Figure 8**

## Step 3 Check Results

When a task fails, a notification will be sent to the user ID registered in the `TELEGRAM_CHAT_ID` variable. The result will be:

![Alt Text](/pic/result_1.png)

**Figure 9**

When the DAG runs successfully, the last task will execute, sending a success notification:

![Alt Text](/pic/result_2.png)

**Figure 10**


**That all, happy experimenting!**
