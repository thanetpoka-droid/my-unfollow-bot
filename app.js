let notFollowingBackList = [];

// ฟังก์ชันตรวจสอบรายชื่อจากไฟล์ JSON
document.getElementById('checkBtn').addEventListener('click', async () => {
    const followersFileInput = document.getElementById('followersFile').files[0];
    const followingFileInput = document.getElementById('followingFile').files[0];

    if (!followersFileInput || !followingFileInput) {
        alert('❌ กรุณาเลือกไฟล์ทั้ง Followers และ Following ให้ครบถ้วนก่อนครับ');
        return;
    }

    try {
        const followersData = JSON.parse(await followersFileInput.text());
        const followingData = JSON.parse(await followingFileInput.text());

        const followers = new Set();
        const following = new Set();

        // ฟังก์ชันกวาดหา Username จาก JSON ทุกรูปแบบ
        function extractUsernames(data, targetSet) {
            if (typeof data === 'object' && data !== null) {
                for (let key in data) {
                    if (key === 'value' && typeof data[key] === 'string') {
                        targetSet.add(data[key]);
                    } else if (key === 'title' && typeof data[key] === 'string') {
                        targetSet.add(data[key]);
                    } else {
                        extractUsernames(data[key], targetSet);
                    }
                }
            } else if (Array.isArray(data)) {
                data.forEach(item => extractUsernames(item, targetSet));
            }
        }

        extractUsernames(followersData, followers);
        extractUsernames(followingData, following);

        // คำนวณหาคนที่ไม่ฟอลกลับ
        notFollowingBackList = [...following].filter(username => !followers.has(username)).sort();

        // แสดงผลลัพธ์บนหน้าเว็บ
        document.getElementById('followingCount').innerText = following.size;
        document.getElementById('followersCount').innerText = followers.size;
        document.getElementById('notBackCount').innerText = notFollowingBackList.length;

        const userListUl = document.getElementById('userList');
        userListUl.innerHTML = '';
        notFollowingBackList.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user;
            userListUl.appendChild(li);
        });

        document.getElementById('resultSection').classList.remove('hidden');
        alert('🎉 ตรวจสอบข้อมูลสำเร็จ!');

    } catch (error) {
        console.error(error);
        alert('❌ เกิดข้อผิดพลาดในการอ่านไฟล์ JSON กรุณาตรวจสอบรูปแบบไฟล์อีกครั้ง');
    }
});

// ฟังก์ชันดาวน์โหลดไฟล์ target_users.txt
document.getElementById('downloadTxtBtn').addEventListener('click', () => {
    if (notFollowingBackList.length === 0) {
        alert('❌ ไม่มีรายชื่อสำหรับดาวน์โหลด');
        return;
    }
    const blob = new Blob([notFollowingBackList.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'target_users.txt';
    a.click();
    URL.revokeObjectURL(url);
});

// ฟังก์ชันปุ่มเริ่มอันฟอลผ่านเว็บ (ส่งข้อมูลให้ server.py รัน Python ต่อทันที)
document.getElementById('startUnfollowBtn').addEventListener('click', async () => {
    if (notFollowingBackList.length === 0) {
        alert('❌ ไม่มีรายชื่อเป้าหมายสำหรับอันฟอล');
        return;
    }

    if (!confirm(`ยืนยันการเริ่มอันฟอลทั้งหมด ${notFollowingBackList.length} บัญชี?`)) return;

    try {
        const res = await fetch('/start-unfollow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ users: notFollowingBackList })
        });
        const data = await res.json();
        if (data.status === 'started') {
            alert(`🚀 ส่งรายชื่อ ${data.count} บัญชีไปที่ Python สำเร็จ! บอทกำลังเริ่มทำงานแล้ว`);
        }
    } catch (err) {
        console.error(err);
        alert('❌ ไม่สามารถเชื่อมต่อกับ Server ได้ (ตรวจสอบให้แน่ใจว่าเปิดเว็บผ่าน http://127.0.0.1:8000 และรัน python3 server.py อยู่)');
    }
});