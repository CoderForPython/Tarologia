from flask import Flask, render_template_string, jsonify, request
import json
import random
from pathlib import Path
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# === КОНФИГУРАЦИЯ ===
BASE_DIR = Path(__file__).parent.absolute()
CARDS_DIR = BASE_DIR / "tarot_cards"
JSON_FILE = BASE_DIR / "tarot_cards.json"
USERS_DB_FILE = BASE_DIR / "users_db.json"

with open(JSON_FILE, "r", encoding="utf-8") as f:
    all_cards = json.load(f)

playable_cards = [c for c in all_cards if c['file'] not in ["CardBacks.png", "cardBorder.png"]]
back_file = "CardBacks.png"

PREDICTIONS = {
    "Шут": "🌟 Время новых начинаний. Сделайте шаг в неизвестность.",
    "Маг": "🔮 У вас есть все ресурсы. Сосредоточьте волю и действуйте.",
    "Жрица": "🌙 Доверьтесь интуиции. Ответы придут из глубины подсознания.",
    "Императрица": "🌸 Период расцвета и созидания. Окружите себя красотой.",
    "Император": "🏰 Время навести порядок. Дисциплина — ваш главный союзник.",
    "Иерофант": "📚 Обратитесь к традициям или мудрому наставнику.",
    "Влюбленные": "💖 Важный выбор сердца. Найдите гармонию.",
    "Колесница": "⚡️ Рывок вперед и победа! Вы полностью контролируете ситуацию.",
    "Сила": "🦁 Мягкая сила и терпение победят любой конфликт.",
    "Отшельник": "🕯️ Время тишины и самопознания. Отойдите от суеты.",
    "Колесо Фортуны": "🎡 Жизнь готовит поворот. Будьте готовы поймать удачу.",
    "Справедливость": "⚖️ Честность и баланс. Ситуация разрешится справедливо.",
    "Повешенный": "🙏 Взгляните на мир иначе. Пауза необходима.",
    "Смерть": "🦋 Время трансформации. Старое уходит, освобождая место новому.",
    "Умеренность": "🌊 Найдите золотую середину. Баланс исцелит всё.",
    "Дьявол": "⛓️ Осознайте свои зависимости. Пора разорвать цепи.",
    "Башня": "⚡️ Крах иллюзий необходим для постройки крепкого будущего.",
    "Звезда": "✨ Надежда и вдохновение. Ваша путеводная звезда светит ярко.",
    "Луна": "🌙 Остерегайтесь обмана. Слушайте интуицию.",
    "Солнце": "☀️ Полный успех и радость! Ваше счастье заразительно.",
    "Суд": "📯 Время пробуждения. Оставьте прошлое позади.",
    "Мир": "🌍 Гармония и завершение пути. Вы на своем месте.",
    "Кубков": "🍷 Эмоциональный подъем, любовь и новые чувства.",
    "Пентаклей": "💰 Финансовый успех, стабильность и земные радости.",
    "Мечей": "🗡️ Ясность ума, решение проблем через логику.",
    "Жезлов": "🔥 Всплеск энергии, страсть и новые начинания."
}

def get_text(card_name):
    for key in PREDICTIONS:
        if key in card_name: return PREDICTIONS[key]
    return "✨ Звезды сегодня благосклонны к вам. Доверьтесь судьбе."

def load_db():
    if USERS_DB_FILE.exists():
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==================== ИНТЕРФЕЙС ====================
HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Tarot Deck ✨</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0518; color:#fff; font-family: 'Segoe UI', sans-serif; height:100vh; overflow:hidden; }
        
        .table {
            position: relative; width: 100%; height: 100vh;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            perspective: 2000px;
        }

        .deck-container {
            position: absolute; bottom: 60px;
            width: 160px; height: 260px;
            transform-style: preserve-3d;
            transition: transform 1s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.8s;
            cursor: pointer;
        }

        .card-in-deck {
            position: absolute; width: 160px; height: 260px;
            border-radius: 12px; border: 1px solid #ffd966;
            background-image: url('/cards/{{back_file}}'); background-size: cover;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            transition: transform 0.8s cubic-bezier(0.23, 1, 0.32, 1);
        }

        @keyframes shuffle-anim {
            0% { transform: translate(0, 0) rotate(0); }
            25% { transform: translate(-140px, -220px) rotate(-20deg); }
            50% { transform: translate(140px, -270px) rotate(20deg); }
            75% { transform: translate(0, -120px) rotate(0); }
            100% { transform: translate(0, 0) rotate(0); }
        }
        .shuffling { animation: shuffle-anim 0.8s ease-in-out infinite; }

        .result-card {
            position: absolute; width: 220px; height: 350px;
            bottom: 60px; left: 50%; margin-left: -110px;
            transform-style: preserve-3d;
            transition: transform 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), bottom 1.2s ease, opacity 0.5s;
            z-index: 100; opacity: 0; pointer-events: none;
        }
        .result-card.active { 
            bottom: 30%; opacity: 1; pointer-events: auto;
            transform: scale(1.1);
        }

        .card-inner {
            position: relative; width: 100%; height: 100%;
            transform-style: preserve-3d; transition: transform 0.8s;
            border-radius: 15px; border: 2px solid #ffd966;
        }
        .flipped .card-inner { transform: rotateY(180deg); }
        
        .side {
            position: absolute; inset: 0; backface-visibility: hidden;
            border-radius: 13px; background-size: cover; background-position: center;
        }
        .back { background-image: url('/cards/{{back_file}}'); }
        .front { transform: rotateY(180deg); }

        .deck-hide { transform: translateY(500px) !important; opacity: 0; }

        .modal {
            display:none; position:fixed; inset:0; background:rgba(0,0,0,0.9);
            z-index:1000; align-items:center; justify-content:center;
        }
        .modal-box { background:#1a0f2e; border:2px solid #ffd966; padding:30px; border-radius:25px; text-align:center; max-width:400px; }
        
        button { background:#ffd966; color:#000; border:none; padding:12px 25px; border-radius:30px; font-weight:bold; cursor:pointer; margin-top:15px; }
        
        .login-overlay { position:fixed; inset:0; background:#0a0518; z-index:2000; display:flex; align-items:center; justify-content:center; }
        .login-box { text-align:center; padding:40px; border:1px solid #ffd966; border-radius:20px; background:#1a0f2e; }
        input { padding:12px; margin:20px 0; border-radius:10px; width:100%; background:#000; color:#fff; border:1px solid #ffd966; text-align:center; }
    </style>
</head>
<body>
    <div class="login-overlay" id="loginOverlay">
        <div class="login-box">
            <h2 style="color:#ffd966">Введите ваше имя</h2>
            <input type="text" id="username" placeholder="Имя...">
            <button onclick="login()">Войти</button>
        </div>
    </div>

    <div class="table">
        <h2 id="msg" style="position:absolute; top:10%; color:#ffd966; text-align:center; width:100%;">Нажмите на колоду, чтобы начать</h2>
        
        <div class="deck-container" id="deck" onclick="startAutomaticShuffle()">
            </div>
    </div>

    <div class="modal" id="modal">
        <div class="modal-box">
            <h2 id="mTitle" style="color:#ffd966; margin-bottom:15px;"></h2>
            <p id="mText" style="line-height:1.6; font-size:18px;"></p>
            <button onclick="document.getElementById('modal').style.display='none'">Принять</button>
        </div>
    </div>

    <script>
        let user = "";
        let selectedCard = null;
        let isOpened = false;
        let isProcessing = false;

        function login() {
            user = document.getElementById('username').value.trim();
            if(!user) return;
            fetch('/api/login', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({username:user})
            }).then(r => r.json()).then(data => {
                document.getElementById('loginOverlay').style.display = 'none';
                if(data.selected_card) {
                    selectedCard = data.selected_card;
                    isOpened = data.card_opened;
                    document.getElementById('deck').style.display = 'none';
                    showResultCard(selectedCard, isOpened, true);
                } else {
                    initDeck();
                }
            });
        }

        function initDeck() {
            const deck = document.getElementById('deck');
            deck.innerHTML = '';
            for(let i=0; i<10; i++) {
                const c = document.createElement('div');
                c.className = 'card-in-deck';
                c.style.bottom = (i*2) + 'px';
                c.style.zIndex = i;
                deck.appendChild(c);
            }
        }

        function startAutomaticShuffle() {
            if(isProcessing) return;
            isProcessing = true;
            document.getElementById('deck').style.cursor = "default";
            document.getElementById('msg').innerText = "Тасуем судьбу...";
            
            const cards = document.querySelectorAll('.card-in-deck');
            
            // 1. Запуск анимации фонтана
            cards.forEach((c, i) => {
                setTimeout(() => c.classList.add('shuffling'), i * 60);
            });

            // 2. Ровно через 3 секунды останавливаем сами
            setTimeout(() => {
                cards.forEach(c => c.classList.remove('shuffling'));
                document.getElementById('msg').innerText = "Карты ложатся в стопку...";
                
                // 3. Ждем еще 2 секунды тишины (пауза)
                setTimeout(() => {
                    document.getElementById('msg').innerText = "Колода готова. Кликни, чтобы вытянуть карту!";
                    document.getElementById('deck').style.cursor = "pointer";
                    document.getElementById('deck').onclick = drawCard;
                    isProcessing = false;
                }, 2000);

            }, 3000); 
        }

        function drawCard() {
            document.getElementById('deck').onclick = null;
            fetch('/api/draw', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({username:user})
            }).then(r => r.json()).then(data => {
                selectedCard = data.selected_card;
                document.getElementById('msg').innerText = "";
                document.getElementById('deck').classList.add('deck-hide');
                
                const resCard = showResultCard(selectedCard, false, false);
                setTimeout(() => {
                    resCard.classList.add('active');
                }, 100);
            });
        }

        function showResultCard(card, opened, instant) {
            const res = document.createElement('div');
            res.className = `result-card ${opened?'flipped':''} ${instant?'active':''}`;
            res.id = "mainCard";
            res.innerHTML = `
                <div class="card-inner">
                    <div class="side front" style="background-image:url('/cards/${card.file}')"></div>
                    <div class="side back"></div>
                </div>
            `;
            res.onclick = openCard;
            document.querySelector('.table').appendChild(res);
            return res;
        }

        function openCard() {
            if(isOpened) { showPrediction(); return; }
            document.getElementById('mainCard').classList.add('flipped');
            isOpened = true;
            fetch('/api/open', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({username:user})
            });
            setTimeout(showPrediction, 800);
        }

        function showPrediction() {
            fetch('/api/predict', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({card_name:selectedCard.name})
            }).then(r => r.json()).then(data => {
                document.getElementById('mTitle').innerText = selectedCard.name;
                document.getElementById('mText').innerText = data.text;
                document.getElementById('modal').style.display = 'flex';
            });
        }
    </script>
</body>
</html>
"""

# ... (API секция остается без изменений, она работает корректно) ...
@app.route('/')
def index(): return render_template_string(HTML, back_file=back_file)

@app.route('/api/login', methods=['POST'])
def api_login():
    name = request.json.get('username')
    db = load_db()
    if name not in db: db[name] = {'selected_card': None, 'card_opened': False, 'last_reading': None}
    user = db[name]
    if user.get('last_reading'):
        if datetime.fromisoformat(user['last_reading']).date() < datetime.now().date():
            user.update({'selected_card': None, 'card_opened': False, 'last_reading': None})
    save_db(db)
    return jsonify(user)

@app.route('/api/draw', methods=['POST'])
def api_draw():
    name = request.json.get('username'); db = load_db()
    card = random.choice(playable_cards)
    db[name].update({'selected_card': card, 'card_opened': False, 'last_reading': datetime.now().isoformat()})
    save_db(db); return jsonify(db[name])

@app.route('/api/open', methods=['POST'])
def api_open():
    name = request.json.get('username'); db = load_db()
    db[name]['card_opened'] = True; save_db(db); return jsonify({'ok': True})

@app.route('/api/predict', methods=['POST'])
def api_predict():
    return jsonify({'text': get_text(request.json.get('card_name'))})

@app.route('/cards/<path:filename>')
def serve_cards(filename):
    from flask import send_from_directory
    return send_from_directory(str(CARDS_DIR), filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)