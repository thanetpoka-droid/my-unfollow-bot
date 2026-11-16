import json
import os

def find_not_following_back():
    followers_file = 'followers_1.json'
    
    # ค้นหาไฟล์ following ที่ขึ้นต้นด้วยคำว่า following ในโฟลเดอร์
    following_file = None
    for f in os.listdir('.'):
        if 'following' in f and f.endswith('.json'):
            following_file = f
            break

    if not os.path.exists(followers_file) or not following_file:
        print(f"❌ ไม่พบไฟล์ followers_1.json หรือไฟล์ following.json")
        print(f"กรุณานำไฟล์ทั้งสองมาวางไว้ในโฟลเดอร์ ig_manager_bot ก่อนครับ")
        return

    print("📖 กำลังอ่านข้อมูลผู้ติดตาม (Followers)...")
    with open(followers_file, 'r', encoding='utf-8') as f:
        followers_data = json.load(f)

    print(f"📖 กำลังอ่านข้อมูลที่คุณกำลังติดตาม ({following_file})...")
    with open(following_file, 'r', encoding='utf-8') as f:
        following_data = json.load(f)

    followers = set()
    following = set()

    # ฟังก์ชันช่วยกวาดหา Username จากโครงสร้าง JSON ทุกรูปแบบ
    def extract_usernames(data, target_set):
        if isinstance(data, dict):
            for k, v in data.items():
                if k == 'value' and isinstance(v, str):
                    target_set.add(v)
                elif k == 'title' and isinstance(v, str):
                    target_set.add(v)
                else:
                    extract_usernames(v, target_set)
        elif isinstance(data, list):
            for item in data:
                extract_usernames(item, target_set)

    extract_usernames(followers_data, followers)
    extract_usernames(following_data, following)

    # หาคนที่เราติดตาม แต่เขาไม่ได้ติดตามเรากลับ
    not_following_back = sorted(list(following - followers))

    print(f"\n-------------------------------------------------------")
    print(f"👥 คุณติดตามทั้งหมด: {len(following)} บัญชี")
    print(f"👤 คนที่ติดตามคุณ: {len(followers)} บัญชี")
    print(f"🔍 พบผู้ที่ไม่ฟอลโลว์คุณกลับ: {len(not_following_back)} บัญชี")
    print(f"-------------------------------------------------------")

    # บันทึกลงไฟล์ target_users.txt
    with open('target_users.txt', 'w', encoding='utf-8') as f:
        for username in not_following_back:
            f.write(f"{username}\n")

    print("🎉 บันทึกรายชื่อคนที่ไม่ฟอลกลับลงใน target_users.txt สำเร็จแล้ว!")
    print("💡 ขั้นตอนต่อไปรันคำสั่ง: python3 unfollow_bot.py เพื่อเริ่มเลิกติดตาม")

if __name__ == "__main__":
    find_not_following_back()