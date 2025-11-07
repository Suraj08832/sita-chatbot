import os
import logging
import tempfile

logger = logging.getLogger(__name__)

# Try to import TensorFlow dependencies
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    from tensorflow import keras
    import numpy as np
    from PIL import Image
    TENSORFLOW_AVAILABLE = True
except ImportError as e:
    logger.warning(f"TensorFlow not available: {e}. NSFW detection will be disabled.")
    TENSORFLOW_AVAILABLE = False
    tf = None
    hub = None
    keras = None
    np = None
    Image = None

# Model path relative to resources folder
# From helper_funcs: go up to modules, then up to sitaBot, then to resources
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'nsfw_model', 'nsfw_mobilenet2.224x224.h5')
# Normalize the path
MODEL_PATH = os.path.normpath(MODEL_PATH)
IMAGE_DIM = 224

# Load Model
model = None

def load_model():
    """Load the NSFW detection model"""
    if not TENSORFLOW_AVAILABLE:
        return None
    try:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model file not found: {MODEL_PATH}")
            return None
        return tf.keras.models.load_model(MODEL_PATH, custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
    except Exception as e:
        logger.error(f"Failed to load NSFW model: {e}")
        return None

if TENSORFLOW_AVAILABLE:
    model = load_model()

def classify(model, image_path):
    """Classify an image for NSFW content"""
    if not model or not TENSORFLOW_AVAILABLE:
        return None
    try:
        img = keras.preprocessing.image.load_img(image_path, target_size=(IMAGE_DIM, IMAGE_DIM))
        img = keras.preprocessing.image.img_to_array(img) / 255.0
        img = np.expand_dims(img, axis=0)
        
        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
        predictions = model.predict(img)[0]
        
        # Only remove if file exists and is a temp file
        if os.path.exists(image_path) and tempfile.gettempdir() in image_path:
            try:
                os.remove(image_path)
            except:
                pass
        
        return {category: float(predictions[i]) for i, category in enumerate(categories)}
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return None

def detect_nsfw(image_path):
    """Detect NSFW content in an image"""
    if not model:
        return None
    return classify(model, image_path)
