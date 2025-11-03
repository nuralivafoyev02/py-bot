import os
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()  # .env fayldan o'qish

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise RuntimeError("TELEGRAM_TOKEN yoki TELEGRAM_CHAT_ID .env faylda mavjud emas!")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change_this_in_prod")  # flash uchun

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send():
    # Formdan kelgan maydonlar
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    message_text = request.form.get("message", "").strip()

    # Minimal validatsiya
    if not (name or phone or message_text):
        flash("Iltimos — kamida bitta maydonni to'ldiring.", "error")
        return redirect(url_for("index"))

    # Telegramga yuboriladigan matnni tayyorlash
    telegram_message = f"📩 Yangi forma yuborildi:\n\n"
    if name:
        telegram_message += f"👤 Ism: {name}\n"
    if phone:
        telegram_message += f"📞 Telefon: {phone}\n"
    if message_text:
        telegram_message += f"✉️ Xabar: {message_text}\n"

    payload = {
        "chat_id": CHAT_ID,
        "text": telegram_message,
        "parse_mode": "HTML"
    }

    resp = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)

    if resp.status_code == 200:
        flash("Xabar muvaffaqiyatli yuborildi ✅", "success")
    else:
        # Telegram xatolikni batafsil ko'rsatish (dev uchun foydali)
        flash(f"Xato yuborishda: {resp.status_code} — {resp.text}", "error")

    return redirect(url_for("index"))

# API uslubi - AJAX bilan yuborish uchun JSON natija qaytaruvchi endpoint (ixtiyoriy)
@app.route("/api/send", methods=["POST"])
def api_send():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    message_text = (data.get("message") or "").strip()

    if not (name or phone or message_text):
        return jsonify({"ok": False, "error": "Empty payload"}), 400

    telegram_message = f"📩 Yangi forma (API):\n\n"
    if name:
        telegram_message += f"👤 Ism: {name}\n"
    if phone:
        telegram_message += f"📞 Telefon: {phone}\n"
    if message_text:
        telegram_message += f"✉️ Xabar: {message_text}\n"

    payload = {"chat_id": CHAT_ID, "text": telegram_message, "parse_mode": "HTML"}
    resp = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)

    if resp.status_code == 200:
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False, "error": resp.text}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
