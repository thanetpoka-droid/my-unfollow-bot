import os
import random
import time
from playwright.sync_api import sync_playwright

# ตั้งค่าความปลอดภัย (Safety Settings)
MAX_UNFOLLOW_PER_RUN = 70   # จำกัดจำนวนสูงสุดต่อการรัน 1 ครั้ง (แนะนำไม่เกิน 10-20)
MIN_DELAY_SEC = 10         # เวลาหน่วงขั้นต่ำต่อ 1 คน (วินาที)
MAX_DELAY_SEC = 18       # เวลาหน่วงสูงสุดต่อ 1 คน (วินาที)
SESSION_DIR = "./instagram_session"  # โฟลเดอร์สำหรับเก็บบันทึกการล็อกอิน

def load_targets(filename='target_users.txt'):
    if not os.path.exists(filename):
        print(f"❌ ไม่พบไฟล์ {filename} กรุณารันสร้างไฟล์รายชื่อก่อน")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_remaining_targets(remaining_users, filename='target_users.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for user in remaining_users:
            f.write(f"{user}\n")

def run_unfollow_bot():
    targets = load_targets()
    if not targets:
        print("ไม่มีรายชื่อเป้าหมายใน target_users.txt")
        return

    print(f"📋 พบรายชื่อเป้าหมายทั้งหมด {len(targets)} บัญชี")
    print(f"🛡️ ระบบจะทำงานสูงสุด {MAX_UNFOLLOW_PER_RUN} บัญชีในรอบนี้เพื่อความปลอดภัย\n")

    with sync_playwright() as p:
        # ใช้ launch_persistent_context เพื่อจำการล็อกอินอัตโนมัติ
        print("🌐 กำลังเปิดเบราว์เซอร์...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            slow_mo=60,
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        page.goto("https://www.instagram.com/")

        print("\n=======================================================")
        print("1. หากระบบยังไม่ได้ล็อกอิน ให้ทำการล็อกอิน Instagram ให้เรียบร้อย")
        print("2. (หากเคยล็อกอินแล้ว ระบบจะข้ามขั้นตอนี้ให้อัตโนมัติ)")
        print("3. เมื่อพร้อมแล้ว ให้กดปุ่ม [Enter] ที่หน้าต่าง Terminal นี้เพื่อเริ่มทำงาน")
        print("=======================================================")
        input()

        processed_count = 0
        remaining_targets = list(targets)

        for username in targets:
            if processed_count >= MAX_UNFOLLOW_PER_RUN:
                print(f"\n🛑 ครบโควตาความปลอดภัย ({MAX_UNFOLLOW_PER_RUN} บัญชี/รอบ) หยุดการทำงานอัตโนมัติ")
                break

            try:
                processed_count += 1
                print(f"[{processed_count}/{min(len(targets), MAX_UNFOLLOW_PER_RUN)}] กำลังเข้าโปรไฟล์: {username}")
                page.goto(f"https://www.instagram.com/{username}/", timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(random.uniform(3, 5))

                # ค้นหาปุ่ม "กำลังติดตาม" หรือ "Following" (รองรับทั้ง button และ div)
                following_btn = page.locator("button:has-text('กำลังติดตาม'), button:has-text('Following'), div[role='button']:has-text('Following'), div[role='button']:has-text('กำลังติดตาม')").first

                if following_btn.count() > 0:
                    following_btn.click()
                    time.sleep(random.uniform(2, 3.5))

                    # ค้นหาปุ่มยืนยัน "เลิกติดตาม" หรือ "Unfollow"
                    confirm_btn = page.locator("button:has-text('เลิกติดตาม'), button:has-text('Unfollow'), div[role='button']:has-text('Unfollow'), div[role='button']:has-text('เลิกติดตาม'), span:text-is('Unfollow'), span:text-is('เลิกติดตาม')").first
                    if confirm_btn.count() > 0:
                        confirm_btn.click()
                        print(f"   ✅ เลิกติดตาม {username} สำเร็จ")
                    else:
                        print(f"   ⚠️ ไม่พบปุ่มยืนยันสำหรับ {username} (ข้าม)")
                else:
                    print(f"   ℹ️ ไม่พบปุ่มกำลังติดตามสำหรับ {username} (อาจเลิกติดตามไปแล้ว)")

                # ลบรายชื่อที่ดำเนินการแล้วออกจากคิวและอัปเดตไฟล์ทันที
                remaining_targets.remove(username)
                save_remaining_targets(remaining_targets)

                if processed_count < min(len(targets), MAX_UNFOLLOW_PER_RUN):
                    wait_sec = random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC)
                    print(f"   ⏳ พักหน่วงเวลา {wait_sec:.1f} วินาที...\n")
                    time.sleep(wait_sec)

            except Exception as e:
                print(f"   ❌ เกิดข้อผิดพลาดกับ {username}: {e}")
                print("   หยุดการทำงานชั่วคราวเพื่อความปลอดภัย")
                break

        print("\n🎉 เสร็จสิ้นการทำงาน! รายชื่อที่เหลือถูกบันทึกไว้ใน target_users.txt สำหรับรันรอบถัดไป")
        context.close()

if __name__ == "__main__":
    run_unfollow_bot()