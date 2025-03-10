import requests
import os

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# GitHubの未読通知を取得する関数
def get_unread_github_notifications():
    url = 'https://api.github.com/notifications'
    headers = {
        'Authorization': f'token {GITHUB_ACCESS_TOKEN}',
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching notifications: {response.status_code}")
        return []

# Discordにメッセージを送信する関数
def send_to_discord(embed):
    payload = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
    
    if response.status_code == 204:
        print("Successfully sent message to Discord!")
    else:
        print(f"Error sending message to Discord: {response.status_code}")

# GitHubの通知を既読にする関数
def mark_notification_as_read(thread_id):
    url = f'https://api.github.com/notifications/threads/{thread_id}'
    headers = {
        'Authorization': f'token {GITHUB_ACCESS_TOKEN}',
    }
    response = requests.patch(url, headers=headers)
    
    if response.status_code == 205:
        print(f"Notification {thread_id} marked as read.")
    else:
        print(f"Error marking notification {thread_id} as read: {response.status_code}")

# 通知を確認し、未読通知をDiscordに送信し、既読にする関数
def check_and_notify():
    notifications = get_unread_github_notifications()
    
    for notification in notifications:
        notif_type = notification["subject"]["type"]
        reason = notification["reason"]

        # Issue または PullRequest のコメント通知のみ処理
        if notif_type in ["PullRequest", "Issue"] and reason == "comment":
            title = notification["subject"]["title"]
            repo = notification["repository"]["full_name"]
            url = notification["subject"]["url"]

            # Discord 埋め込みメッセージ作成
            embed = {
                "title": f"💬 {title}",
                "url": url.replace("api.github.com", "github.com").replace("repos/", ""),
                "color": 3447003,  # 青色
                "footer": {
                    "text": repo
                }
            }

            send_to_discord(embed)
            
            # 通知を既読にする
            thread_id = notification['id']
            mark_notification_as_read(thread_id)

if __name__ == "__main__":
    check_and_notify()
