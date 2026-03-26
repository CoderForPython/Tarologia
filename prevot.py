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

if not JSON_FILE.exists():
    all_cards = []
else:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        all_cards = json.load(f)

# Фильтруем системные изображения
playable_cards = [c for c in all_cards if c['file'] not in ["CardBacks.png", "cardBorder.png"]]
back_file = "CardBacks.png"

# === ПОЛНЫЙ СПИСОК ПРЕДСКАЗАНИЙ (78 КАРТ) ===
PREDICTIONS = {
    # Старшие Арканы
    "Шут": "🌟 Время обнуления. Не бойтесь выглядеть глупо, делайте шаг в неизвестность — судьба подстелет соломку.",
    "Маг": "🔮 У вас есть все ресурсы для успеха. Манипулируйте обстоятельствами в свою пользу, сейчас вы мастер игры.",
    "Верховная Жрица": "🌙 Тайное станет явным. Не торопите события, слушайте интуицию и сны — в них ключ к разгадке.",
    "Императрица": "🌸 Период процветания. Отличное время для покупок в дом, заботы о себе и реализации творческих идей.",
    "Император": "🏰 Проявите твердость. Наведите порядок в делах и финансах. Мужчина или начальник окажет поддержку.",
    "Иерофант": "📚 Действуйте по совести. Хороший день для обучения, обращения к традициям или получения совета от мудреца.",
    "Влюбленные": "💖 Предстоит выбор по сердцу. Гармония в отношениях возможна, если вы будете честны в своих желаниях.",
    "Колесница": "⚡️ Рывок вперед! Победа близка, если удержите контроль над эмоциями. Возможна поездка или покупка авто.",
    "Сила": "🦁 Победите врагов мягкостью. Ваше терпение и внутренняя уверенность сейчас эффективнее любой грубой силы.",
    "Отшельник": "🕯️ Уйдите в тень на время. Пауза поможет понять, куда двигаться дальше. Мудрость важнее суеты.",
    "Колесо Фортуны": "🎡 Удача на пороге! Цикл меняется в вашу пользу. Будьте готовы быстро ловить шанс, пока он есть.",
    "Справедливость": "⚖️ Получите то, что заслужили. Юридические дела решатся честно. Соблюдайте баланс во всём.",
    "Повешенный": "🙏 Ситуация зависла. Принесите малую жертву (время или амбиции), чтобы увидеть выход из тупика.",
    "Смерть": "🦋 Время прощаться со старым. То, что уходит, освобождает место для чего-то по-настоящему великого.",
    "Умеренность": "🌊 Спокойствие и мера. Не спешите, лечитесь отдыхом и гармонией. Всё придет в свое время.",
    "Дьявол": "⛓️ Осторожно с искушениями! Возможна зависимость от денег, секса или чужого мнения. Вы свободнее, чем кажется.",
    "Башня": "💥 Крах иллюзий. Старые планы рушатся, но это единственный способ построить что-то действительно прочное.",
    "Звезда": "✨ Ваша надежда оправдана. Свет в конце туннеля стал ярче. Верьте в свою мечту — она сбудется.",
    "Луна": "🌙 Остерегайтесь обмана и скрытых мотивов. Вокруг много тумана, не принимайте важных решений в темноте.",
    "Солнце": "☀️ Триумф, радость и ясность! Огромный успех в делах, счастье в семье и прилив жизненных сил.",
    "Суд": "📯 Пробуждение и итоги. Важный этап завершен, пора расправить крылья и оставить прошлое позади.",
    "Мир": "🌍 Вы на своем месте. Полная гармония с миром, успех в международных делах или долгожданное завершение пути.",

    # Кубки
    "Туз Кубков": "🍷 Поток любви и вдохновения. Новое чувство или эмоциональное обновление.",
    "2 Кубков": "🥂 Идеальное партнерство. Свидание, примирение или успешный договор.",
    "3 Кубков": "🥳 Праздник в кругу друзей. Время радости, беззаботности и хороших новостей.",
    "4 Кубков": "😒 Пресыщение и скука. Вы не замечаете подарок судьбы, потому что зациклены на плохом.",
    "5 Кубков": "😢 Скорбь о потерянном. Перестаньте смотреть на разбитые чаши, сзади стоят полные.",
    "6 Кубков": "🧸 Привет из прошлого. Встреча со старым другом или теплые ностальгические воспоминания.",
    "7 Кубков": "🌈 Мир иллюзий. Выбирайте осторожно, не всё то золото, что блестит в ваших мечтах.",
    "8 Кубков": "👣 Время уходить. Вы переросли эту ситуацию, пора искать что-то более глубокое.",
    "9 Кубков": "🍰 Исполнение желаний. Наслаждайтесь комфортом и своими достижениями, вы это заслужили.",
    "10 Кубков": "👨‍👩‍👧‍👦 Семейное счастье. Гармония в доме, уют и искренняя поддержка близких людей.",
    "Паж Кубков": "🐟 Милое сообщение или творческий импульс. Доверьтесь своему внутреннему ребенку.",
    "Рыцарь Кубков": "🏇 Романтическое предложение. Кто-то придет к вам с открытым сердцем и добрыми намерениями.",
    "Королева Кубков": "🌊 Слушайте свою душу. Добрая женщина или ваша интуиция помогут найти верный путь.",
    "Король Кубков": "🍷 Эмоциональная стабильность. Проявите сострадание, но не давайте чувствам затопить разум.",

    # Пентакли
    "Туз Пентаклей": "💰 Грандиозный шанс на богатство. Судьба дарит вам золотую монету — вложите её с умом.",
    "2 Пентаклей": "🤹 Ловкое совмещение дел. Балансируйте бюджетом, вы справитесь с любым хаосом.",
    "3 Пентаклей": "🛠 Профессиональный рост. Ваши таланты заметят, работа в команде принесет отличный доход.",
    "4 Пентаклей": "📦 Стабильность и жадность. Деньги под контролем, но не бойтесь тратить на действительно важное.",
    "5 Пентаклей": "🌨 Временный кризис. Попросите помощи, вы не одиноки в своих трудностях.",
    "6 Пентаклей": "🤝 Благотворительность. Вы либо получите заслуженную помощь, либо сами станете меценатом.",
    "7 Пентаклей": "⏳ Время ожидания. Вы посадили семена, теперь наберитесь терпения, урожай скоро созреет.",
    "8 Пентаклей": "📐 Мастерство и труд. Упорная работа над деталями принесет вам признание и стабильный доход.",
    "9 Пентаклей": "💅 Финансовая независимость. Время баловать себя роскошью и наслаждаться плодами труда.",
    "10 Пентаклей": "🏦 Процветание рода. Крупные покупки, наследство или финансовая стабильность семьи.",
    "Паж Пентаклей": "🌱 Хорошие новости о деньгах или учебе. Время закладывать фундамент нового проекта.",
    "Рыцарь Пентаклей": "🚜 Медленный, но верный прогресс. Надежность и практичность — ваши главные козыри сегодня.",
    "Королева Пентаклей": "🧺 Практичность и уют. Позаботьтесь о комфорте и материальных ценностях.",
    "Король Пентаклей": "👑 Успех в бизнесе. Влиятельный покровитель или ваша хватка приведут к большой прибыли.",

    # Мечи
    "Туз Мечей": "🗡 Прояснение ситуации. Режьте лишнее, принимайте волевое решение — правда на вашей стороне.",
    "2 Мечей": "🙈 Тупик и сомнения. Снимите повязку с глаз и сделайте выбор, даже если он болезненный.",
    "3 Мечей": "💔 Горькая правда. Разбитое сердце или обида, которую нужно прожить, чтобы идти дальше.",
    "4 Мечей": "🛌 Время восстановления. Возьмите тайм-аут, отключите телефон и просто выспитесь.",
    "5 Мечей": "⚔️ Пиррова победа. Вы выиграли спор, но потеряли доверие. Подумайте, стоило ли оно того.",
    "6 Мечей": "🛶 Переправа в тихую гавань. Уход от проблем к более спокойным и ясным временам.",
    "7 Мечей": "🦊 Осторожно, хитрость! Кто-то играет не по правилам, или вам самим придется проявить смекалку.",
    "8 Мечей": "🕸 Мнимые ограничения. Вы не в клетке, просто боитесь сделать шаг. Страх — это единственная преграда.",
    "9 Мечей": "😱 Бессонница и тревоги. Ваши страхи преувеличены, утро вечера мудренее.",
    "10 Мечей": "🔚 Конец черной полосы. Хуже уже не будет, теперь только путь наверх.",
    "Паж Мечей": "🔍 Шпионаж или критика. Будьте начеку, проверяйте информацию и не лезьте на рожон.",
    "Рыцарь Мечей": "🏇 Стремительная атака. Резкие перемены, споры или необходимость быстро отстаивать свои границы.",
    "Королева Мечей": "❄️ Холодный рассудок. Проявите независимость и строгость, эмоции сейчас только мешают.",
    "Король Мечей": "👨‍⚖️ Власть интеллекта. Авторитетное мнение, закон или жесткая логика помогут решить вопрос.",

    # Жезлы
    "Туз Жезлов": "🔥 Вспышка энтузиазма! Шанс проявить себя, начать новый проект или зажечь искру в отношениях.",
    "2 Жезлов": "🔭 Планирование экспансии. Мир у ваших ног, пора выбирать направление для следующего шага.",
    "3 Жезлов": "🚢 Уверенность в будущем. Ваши корабли скоро приплывут, вы построили верную стратегию.",
    "4 Жезлов": "🏡 Праздник и стабильность. Радостное событие дома, завершение этапа или заслуженный отдых.",
    "5 Жезлов": "🥊 Здоровая конкуренция. Отстаивайте свои идеи, в споре родится истина и ваш авторитет.",
    "6 Жезлов": "🏇 Триумфатор! Вас ждет признание, похвала и публичный успех. Вы на коне.",
    "7 Жезлов": "🛡 Защита позиций. Против вас могут ополчиться, но вы сильнее. Не сдавайтесь.",
    "8 Жезлов": "🏹 Скорость и новости. События развиваются стремительно, ждите важных известий издалека.",
    "9 Жезлов": "🧱 Последнее усилие. Вы устали, но победа близка. Соберите волю в кулак и доведите дело до конца.",
    "10 Жезлов": "🎒 Тяжелая ноша. Вы взяли на себя слишком много. Пора делегировать обязанности, иначе перегорите.",
    "Паж Жезлов": "✉️ Вдохновляющее известие. Новое хобби или интересное предложение, пробуждающее азарт.",
    "Рыцарь Жезлов": "🏇 Авантюризм и страсть. Смело идите на риск, сейчас время активных и быстрых действий.",
    "Королева Жезлов": "🌻 Харизма и уверенность. Будьте в центре внимания, ваша энергия притягивает людей и удачу.",
    "Король Жезлов": "🔥 Лидерство. Возьмите на себя ответственность, ваша воля способна свернуть горы."
}

def get_text(card_name):
    # Ищем частичное совпадение ключа в названии карты (например "Шут" в "0. Шут")
    for key, val in PREDICTIONS.items():
        if key.lower() in card_name.lower():
            return val
    return "✨ Звезды сегодня благосклонны. Доверьтесь своей интуиции."

def load_db():
    if USERS_DB_FILE.exists():
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# === HTML ИНТЕРФЕЙС ===
HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Tarologia ✨</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0518; color:#fff; font-family: 'Segoe UI', sans-serif; height:100vh; overflow:hidden; }
        .table { position: relative; width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; perspective: 2000px; }
        .deck-container { position: absolute; bottom: 60px; width: 160px; height: 260px; transform-style: preserve-3d; transition: transform 1s; cursor: pointer; }
        .card-in-deck { position: absolute; width: 160px; height: 260px; border-radius: 12px; border: 1px solid #ffd966; background-image: url('/cards/{{back_file}}'); background-size: cover; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: transform 0.8s; }
        @keyframes shuffle-anim { 0% { transform: translate(0, 0) rotate(0); } 25% { transform: translate(-140px, -220px) rotate(-20deg); } 50% { transform: translate(140px, -270px) rotate(20deg); } 75% { transform: translate(0, -120px) rotate(0); } 100% { transform: translate(0, 0) rotate(0); } }
        .shuffling { animation: shuffle-anim 0.8s ease-in-out infinite; }
        .result-card { position: absolute; width: 220px; height: 350px; bottom: 60px; left: 50%; margin-left: -110px; transform-style: preserve-3d; transition: all 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); z-index: 100; opacity: 0; pointer-events: none; }
        .result-card.active { bottom: 30%; opacity: 1; pointer-events: auto; transform: scale(1.1); }
        .card-inner { position: relative; width: 100%; height: 100%; transform-style: preserve-3d; transition: transform 0.8s; border-radius: 15px; border: 2px solid #ffd966; }
        .flipped .card-inner { transform: rotateY(180deg); }
        .side { position: absolute; inset: 0; backface-visibility: hidden; border-radius: 13px; background-size: cover; background-position: center; }
        .back { background-image: url('/cards/{{back_file}}'); }
        .front { transform: rotateY(180deg); }
        .deck-hide { transform: translateY(500px) !important; opacity: 0; }
        .modal { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.9); z-index:1000; align-items:center; justify-content:center; }
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
            <h2 style="color:#ffd966">Представься судьбе</h2>
            <input type="text" id="username" placeholder="Ваше имя...">
            <button onclick="login()">Войти</button>
        </div>
    </div>
    <div class="table">
        <h2 id="msg" style="position:absolute; top:10%; color:#ffd966; text-align:center; width:100%;">Нажми на колоду для начала тасовки</h2>
        <div class="deck-container" id="deck" onclick="startAutomaticShuffle()"></div>
    </div>
    <div class="modal" id="modal">
        <div class="modal-box">
            <h2 id="mTitle" style="color:#ffd966; margin-bottom:15px;"></h2>
            <p id="mText" style="line-height:1.6; font-size:18px;"></p>
            <button onclick="document.getElementById('modal').style.display='none'">Принять</button>
        </div>
    </div>
    <script>
        let user = ""; let selectedCard = null; let isOpened = false; let isProcessing = false;
        function login() {
            user = document.getElementById('username').value.trim();
            if(!user) return;
            fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:user}) })
            .then(r => r.json()).then(data => {
                document.getElementById('loginOverlay').style.display = 'none';
                if(data.selected_card) {
                    selectedCard = data.selected_card; isOpened = data.card_opened;
                    document.getElementById('deck').style.display = 'none';
                    showResultCard(selectedCard, isOpened, true);
                } else { initDeck(); }
            });
        }
        function initDeck() {
            const deck = document.getElementById('deck'); deck.innerHTML = '';
            for(let i=0; i<10; i++) {
                const c = document.createElement('div'); c.className = 'card-in-deck';
                c.style.bottom = (i*2) + 'px'; c.style.zIndex = i; deck.appendChild(c);
            }
        }
        function startAutomaticShuffle() {
            if(isProcessing) return; isProcessing = true;
            document.getElementById('deck').style.cursor = "default";
            document.getElementById('msg').innerText = "Судьба тасует карты...";
            const cards = document.querySelectorAll('.card-in-deck');
            cards.forEach((c, i) => { setTimeout(() => c.classList.add('shuffling'), i * 60); });
            setTimeout(() => {
                cards.forEach(c => c.classList.remove('shuffling'));
                document.getElementById('msg').innerText = "Карты ложатся в колоду...";
                setTimeout(() => {
                    document.getElementById('msg').innerText = "Готово. Жми на колоду, чтобы вытянуть карту!";
                    document.getElementById('deck').style.cursor = "pointer";
                    document.getElementById('deck').onclick = drawCard;
                    isProcessing = false;
                }, 2000);
            }, 3000);
        }
        function drawCard() {
            document.getElementById('deck').onclick = null;
            fetch('/api/draw', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:user}) })
            .then(r => r.json()).then(data => {
                selectedCard = data.selected_card;
                document.getElementById('msg').innerText = "";
                document.getElementById('deck').classList.add('deck-hide');
                const resCard = showResultCard(selectedCard, false, false);
                setTimeout(() => { resCard.classList.add('active'); }, 100);
            });
        }
        function showResultCard(card, opened, instant) {
            const res = document.createElement('div');
            res.className = `result-card ${opened?'flipped':''} ${instant?'active':''}`;
            res.id = "mainCard";
            res.innerHTML = `<div class="card-inner"><div class="side front" style="background-image:url('/cards/${card.file}')"></div><div class="side back"></div></div>`;
            res.onclick = openCard;
            document.querySelector('.table').appendChild(res);
            return res;
        }
        function openCard() {
            if(isOpened) { showPrediction(); return; }
            document.getElementById('mainCard').classList.add('flipped');
            isOpened = true;
            fetch('/api/open', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:user}) });
            setTimeout(showPrediction, 800);
        }
        function showPrediction() {
            fetch('/api/predict', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({card_name:selectedCard.name}) })
            .then(r => r.json()).then(data => {
                document.getElementById('mTitle').innerText = selectedCard.name;
                document.getElementById('mText').innerText = data.text;
                document.getElementById('modal').style.display = 'flex';
            });
        }
    </script>
</body>
</html>
"""

# === API ===
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