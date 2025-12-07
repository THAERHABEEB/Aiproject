# -*- coding: utf-8 -*-
import os
import sys
import logging
import warnings
import time

# إعدادات لإسكات TensorFlow وكل التحذيرات تمامًا
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_USE_LEGACY_KERAS"] = "1"
logging.getLogger('tensorflow').setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# دعم العربية على ويندوز بدون أي مشاكل
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# تأخير بسيط لتجنب تعارض المقابس
time.sleep(0.1)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# استيراد الذكاء الاصطناعي فقط عند الحاجة (Lazy Loading)
_predict_intent = None
_understand_message = None

def get_ai_functions():
    global _predict_intent, _understand_message
    if _predict_intent is None:
        print("جاري تفعيل الذكاء الاصطناعي الملكي... (مرة واحدة فقط)")
        from utils.deep_intent_classifier import predict_intent_deep
        from utils.ai_brain import understand_message
        _predict_intent = predict_intent_deep
        _understand_message = understand_message
        print("الذكاء الاصطناعي جاهز يا جلالة الملك!")

# الصفحات الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

# API التنبؤ بالنية
@app.route('/predict_intent', methods=['POST'])
def predict_intent():
    try:
        get_ai_functions()
        message = request.json.get('message', '').strip()
        if not message:
            return jsonify({'predicted_intent': {'intent': 'unknown', 'confidence': 0.0}}), 400
        
        intent = _predict_intent(message)
        return jsonify({'predicted_intent': intent})
    except Exception as e:
        return jsonify({'predicted_intent': {'intent': 'error', 'error': str(e)}}), 500

# API الدردشة الرئيسية
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        get_ai_functions()
        message = request.json.get('message', '').strip()
        if not message:
            return jsonify({'reply': 'اكتب شيئًا يا ملك!'})

        intent = _predict_intent(message)
        response = _understand_message(message, intent)
        return jsonify(response)
    except Exception as e:
        return jsonify({'reply': 'عذرًا، الذكاء الاصطناعي في قيلولة ملكية... جرب تاني!', 'error': str(e)})

# API المنتجات – يشتغل بدون أي طباعة أو تأخير
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        from utils.ai_brain import products
        category = request.args.get('category', 'all').lower().strip()
        
        filtered = products
        if category and category != 'all':
            filtered = [p for p in products if str(p.get('category', '')).lower() == category]

        return jsonify({
            'success': True,
            'products': [
                {
                    'id': int(p.get('id', 0)),
                    'title': str(p.get('title', 'منتج فاخر')),
                    'price': str(p.get('price', 'غير محدد')),
                    'price_currency': 'جنيه',
                    'image_url': str(p.get('image_url', 'https://via.placeholder.com/300x200/F59E0B/000000?text=نفرتيتي')),
                    'category': str(p.get('category', '')).lower(),
                    'color': str(p.get('color', '')),
                    'brand': str(p.get('brand', 'نفرتيتي كوميرس')),
                    'description': str(p.get('description', 'منتج ملكي فاخر'))
                } for p in filtered
            ],
            'total': len(filtered)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': 'فشل تحميل المنتجات', 'products': []}), 500

# API الفئات
@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        from utils.ai_brain import products
        cats = sorted({str(p.get('category','')).lower().strip() for p in products if p.get('category')})
        return jsonify({'success': True, 'categories': list(cats)})
    except:
        return jsonify({'success': True, 'categories': ['عام', 'أزياء', 'إلكترونيات', 'جمال']})

# تشغيل السيرفر فورًا بدون أي كلام زيادة
if __name__ == '__main__':
    print("نفرتيتي كوميرس جاهز لاستقبال الملوك...")
    print("http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)