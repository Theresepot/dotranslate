import os
import sys
from PyDictionary import PyDictionary

def find_tessdata_dir():
    if sys.platform.startswith('win'):
        possible = [
            r'C:\\Program Files\\Tesseract-OCR\\tessdata',
            r'C:\\Program Files (x86)\\Tesseract-OCR\\tessdata',
        ]
        for p in possible:
            if os.path.isdir(p):
                return p
    else:
        for p in [
            '/usr/share/tesseract-ocr/5/tessdata',
            '/usr/share/tesseract-ocr/4.00/tessdata',
            '/usr/share/tesseract-ocr/tessdata',
        ]:
            if os.path.isdir(p):
                return p
    return None

TESSDATA_DIR = os.environ.get('TESSDATA_PREFIX') or find_tessdata_dir()

class TranslationApp:
    def __init__(self, **kwargs):
        # Import Kivy modules only when the app is instantiated
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.config import Config
from kivy.core.text import Label as CoreLabel
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
# Configure keyboard shortcuts
Config.set('kivy', 'exit_on_escape', '0')
        # Assign imported classes to self for use in methods
        self.App = App
        self.BoxLayout = BoxLayout
        self.Button = Button
        self.TextInput = TextInput
        self.Label = Label
        self.Spinner = Spinner
        self.ScrollView = ScrollView
        self.Window = Window
        self.GridLayout = GridLayout
        self.dp = dp
        self.Clipboard = Clipboard
        self.CoreLabel = CoreLabel
        self.FileChooserListView = FileChooserListView
        self.Popup = Popup
        self.Widget = Widget
        self.ObjectProperty = ObjectProperty
        self.font_path = self._find_font()
        self.file_chooser = None
        self.popup = None
        self.thesaurus = PyDictionary()
        self.enabled_thesaurus_langs = set(['english'])  # Default to English; user can add more
    
    def _find_font(self):
        """Find a suitable font for Chinese characters"""
        # Common font paths on Linux
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # WenQuanYi Zen Hei
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # WenQuanYi Micro Hei
            '/usr/share/fonts/truetype/droid/DroidSansFallback.ttf',  # Droid Sans Fallback
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Liberation Sans
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # DejaVu Sans
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        # If no font found, return None to use system default
        return None
    
    def show_file_chooser(self, instance):
        content = self.BoxLayout(orientation='vertical')
        self.file_chooser = self.FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.png', '*.jpg', '.jpeg', '*.pdf']
        )
        content.add_widget(self.file_chooser)
        
        buttons = self.BoxLayout(size_hint_y=None, height=self.dp(44))
        select_btn = self.Button(text='Select')
        cancel_btn = self.Button(text='Cancel')
        
        select_btn.bind(on_press=self.process_selected_file)
        cancel_btn.bind(on_press=self.dismiss_popup)
        
        buttons.add_widget(select_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        self.popup = self.Popup(title='Select File', content=content, size_hint=(0.9, 0.9))
        self.popup.open()
    
    def dismiss_popup(self, instance):
        if self.popup:
            self.popup.dismiss()
    
    def process_selected_file(self, instance):
        if self.file_chooser and self.file_chooser.selection:
            file_path = self.file_chooser.selection[0]
            self.dismiss_popup(instance)
            
            try:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    text = self.extract_text_from_image(file_path)
                elif file_path.lower().endswith('.pdf'):
                    text = self.extract_text_from_pdf(file_path)
                else:
                    self.result_text.text = "Unsupported file format"
                    return
                
                self.input_text.text = text
            except Exception as e:
                self.result_text.text = f"Error processing file: {str(e)}"
    
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            lang_codes = {
                'English': 'eng',
                'Chinese': 'chi_sim+chi_tra',
                'Russian': 'rus',
                'German': 'deu',
                'French': 'fra',
                'Spanish': 'spa',
                'Italian': 'ita'
            }
            source_lang = self.title_bar.source_lang.text
            lang = lang_codes.get(source_lang, 'eng')
            # --- Always pass tessdata-dir ---
            if not TESSDATA_DIR:
                raise Exception('Tesseract tessdata directory not found. Please install Tesseract and language packs.')
            # Check if all required .traineddata files exist
            for l in lang.split('+'):
                traineddata = os.path.join(TESSDATA_DIR, f'{l}.traineddata')
                if not os.path.isfile(traineddata):
                    raise Exception(f"Tesseract language data '{l}.traineddata' not found in {TESSDATA_DIR}. Please install the required language pack.")
            tessdata_config = f'--tessdata-dir "{TESSDATA_DIR}" -l {lang} --psm 3'
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            text = pytesseract.image_to_string(image, config=tessdata_config)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def build(self):
        # Set minimum window size
        self.Window.minimum_width = self.dp(600)
        self.Window.minimum_height = self.dp(400)
        
        # Main layout
        main_layout = self.BoxLayout(orientation='vertical', spacing=5)
        
        # Custom title bar with language selection
        self.title_bar = CustomTitleBar()
        main_layout.add_widget(self.title_bar)
        
        # Text input area
        input_kwargs = dict(
            multiline=True,
            hint_text='Enter text to translate...',
            size_hint_y=0.4,  # Take 40% of available height
            font_size=16,
            allow_copy=True
        )
        if self.font_path:
            input_kwargs['font_name'] = self.font_path
        self.input_text = self.TextInput(**input_kwargs)
        
        # Translation engine selection and buttons
        engine_layout = self.BoxLayout(
            size_hint_y=None,
            height=self.dp(50),
            spacing=10,
            padding=[10, 5],
            orientation='horizontal',
            # Remove default stretching
            size_hint_x=None,
            width=self.dp(900)  # Fixed width for the button row
        )
        # Engine spinner with fixed size
        self.engine = self.Spinner(
            text='Google',
            values=('Google', 'DuckDuckGo', 'Yandex', 'DeepL'),
            size_hint=(None, None),
            size=(self.dp(150), self.dp(40)),
            pos_hint={'center_y': 0.5}
        )
        # File selection button with fixed size
        file_btn = self.Button(
            text='Select Image/PDF',
            size_hint=(None, None),
            size=(self.dp(150), self.dp(40)),
            pos_hint={'center_y': 0.5}
        )
        file_btn.bind(on_press=self.show_file_chooser)
        # Translate button with fixed size
        translate_btn = self.Button(
            text='Translate',
            size_hint=(None, None),
            size=(self.dp(150), self.dp(40)),
            pos_hint={'center_y': 0.5}
        )
        translate_btn.bind(on_press=self.translate_text)
        # Copy button with fixed size
        copy_btn = self.Button(
            text='Copy Translation',
            size_hint=(None, None),
            size=(self.dp(150), self.dp(40)),
            pos_hint={'center_y': 0.5}
        )
        copy_btn.bind(on_press=self.copy_translation)
        # Thesaurus language selection button
        thesaurus_btn = self.Button(
            text='Thesaurus Languages',
            size_hint=(None, None),
            size=(self.dp(180), self.dp(40)),
            pos_hint={'center_y': 0.5}
        )
        thesaurus_btn.bind(on_press=self.select_thesaurus_languages)
        # Container to left-align the buttons
        left_buttons = self.BoxLayout(orientation='horizontal', size_hint=(None, 1))
        left_buttons.width = sum([
            self.dp(150),  # engine
            10,
            self.dp(150),  # file_btn
            10,
            self.dp(150),  # translate_btn
            10,
            self.dp(150),  # copy_btn
            10,
            self.dp(180),  # thesaurus_btn
            10
        ])
        left_buttons.spacing = 10
        # Add buttons to left_buttons
        left_buttons.add_widget(self.engine)
        left_buttons.add_widget(file_btn)
        left_buttons.add_widget(translate_btn)
        left_buttons.add_widget(copy_btn)
        left_buttons.add_widget(thesaurus_btn)
        # Add left_buttons to engine_layout
        engine_layout.add_widget(left_buttons)
        # Remove extra flexible spaces
        
        # Result text area
        result_kwargs = dict(
            multiline=True,
            readonly=True,
            hint_text='Translation will appear here...',
            size_hint_y=0.4,  # Take 40% of available height
            font_size=16,
            allow_copy=True
        )
        if self.font_path:
            result_kwargs['font_name'] = self.font_path
        self.result_text = self.TextInput(**result_kwargs)
        
        # Add all widgets to main layout
        main_layout.add_widget(self.input_text)
        main_layout.add_widget(engine_layout)
        main_layout.add_widget(self.result_text)
        
        # Bind swap button
        self.title_bar.swap_btn.bind(on_press=self.swap_languages)
        
        return main_layout
    
    def swap_languages(self, instance):
        # Swap source and target languages
        current_source = self.title_bar.source_lang.text
        self.title_bar.source_lang.text = self.title_bar.target_lang.text
        self.title_bar.target_lang.text = current_source
    
    def translate_text(self, instance):
        text = self.input_text.text
        if not text:
            return
        
        # Map language names to their correct API codes
        language_codes = {
            'english': 'en',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'russian': 'ru',
            'chinese': 'zh',
            'italian': 'it'
        }
        
        # Map engine names to their API identifiers
        engine_codes = {
            'google': 'google',
            'duckduckgo': 'duckduckgo',
            'yandex': 'yandex',
            'deepl': 'deepl'
        }
        
        source_lang = language_codes.get(self.title_bar.source_lang.text.lower(), 'en')
        target_lang = language_codes.get(self.title_bar.target_lang.text.lower(), 'es')
        engine = engine_codes.get(self.engine.text.lower(), 'google')
        
        def chunk_text(text, max_chars):
            # If the text contains CJK (Chinese, Japanese, Korean) characters, split by characters
            cjk_re = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af]')
            if cjk_re.search(text):
                # Split by max_chars characters
                return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            # Otherwise, split by paragraphs, but keep chunks under max_chars
            paragraphs = text.split('\n')
            chunks = []
            current = ''
            for para in paragraphs:
                if len(current) + len(para) + 1 > max_chars:
                    if current:
                        chunks.append(current)
                        current = ''
                if len(para) > max_chars:
                    # If a single paragraph is too long, split it
                    for i in range(0, len(para), max_chars):
                        chunks.append(para[i:i+max_chars])
                else:
                    if current:
                        current += '\n' + para
                    else:
                        current = para
            if current:
                chunks.append(current)
            return chunks
        
        chunks = chunk_text(text, MAX_CHARS)
        translations = []
        
        try:
            for idx, chunk in enumerate(chunks):
                url = "https://translate.librenode.com/api/translate"
                headers = {
                    'Accept': 'application/json'
                }
                payload = {
                    'from': source_lang,
                    'to': target_lang,
                    'engine': engine,
                    'text': chunk
                }
                print(f"Making POST request to: {url} with payload length {len(chunk)}")
                response = requests.post(url, headers=headers, data=payload)
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {response.headers}")
                print(f"Response content: {response.text[:500]}")
                response.raise_for_status()
                try:
                    result = response.json()
                    # Deepl-specific error handling
                    if engine == 'deepl' and (not result.get('translated-text')):
                        translations.append('[Deepl translation failed: No result returned. Try another engine or check API status.]')
                    elif 'translated-text' in result:
                        translations.append(result['translated-text'])
                        # Save word_choices for thesaurus if present
                        if idx == 0 and result.get('word_choices'):
                            self.last_word_choices = result['word_choices']
                        else:
                            self.last_word_choices = None
                    else:
                        translations.append(f"[Chunk {idx+1} failed: Unexpected response format]")
                except json.JSONDecodeError as json_err:
                    translations.append(f"[Chunk {idx+1} error: {str(json_err)}]")
            self.result_text.text = '\n'.join(translations)
            # Thesaurus auto-trigger: only if single word, not Chinese, and language enabled
            result_text = self.result_text.text.strip()
            target_lang = self.title_bar.target_lang.text.lower()
            if (len(result_text.split()) == 1 and
                target_lang != 'chinese' and
                target_lang in self.enabled_thesaurus_langs):
                self.result_text.text = self.get_thesaurus_text(result_text, target_lang)
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                try:
                    error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                    self.result_text.text = f"Error: {error_detail}"
                except json.JSONDecodeError:
                    self.result_text.text = f"Error: {response.text[:100]}"
            else:
                self.result_text.text = f"HTTP Error: {str(http_err)}"
        except requests.exceptions.RequestException as req_err:
            self.result_text.text = f"Request Error: {str(req_err)}"
        except Exception as e:
            self.result_text.text = f"Unexpected Error: {str(e)}"
    
    def copy_translation(self, instance):
        if self.result_text.text:
            self.Clipboard.copy(self.result_text.text)

    def select_thesaurus_languages(self, instance=None):
        # Supported languages (except Chinese)
        supported = ['english', 'spanish', 'french', 'german', 'russian', 'italian']
        content = self.BoxLayout(orientation='vertical', spacing=5)
        checkboxes = {}
        from kivy.uix.checkbox import CheckBox
        for lang in supported:
            row = self.BoxLayout(orientation='horizontal', size_hint_y=None, height=self.dp(40))
            cb = CheckBox(active=(lang in self.enabled_thesaurus_langs))
            checkboxes[lang] = cb
            row.add_widget(cb)
            row.add_widget(self.Label(text=lang.title(), size_hint_x=1))
            content.add_widget(row)
        btn_row = self.BoxLayout(size_hint_y=None, height=self.dp(44))
        save_btn = self.Button(text='Save', size_hint_x=0.5)
        cancel_btn = self.Button(text='Cancel', size_hint_x=0.5)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup = self.Popup(title='Select Thesaurus Languages', content=content, size_hint=(0.6, 0.7))
        def save_cb(instance):
            self.enabled_thesaurus_langs = set(lang for lang, cb in checkboxes.items() if cb.active)
            popup.dismiss()
        save_btn.bind(on_press=save_cb)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def get_thesaurus_text(self, word, lang):
        # For English, use NLTK WordNet
        if lang == 'english':
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet')
            synonyms = []
            antonyms = []
            from nltk.corpus import wordnet
            for syn in wordnet.synsets(word):
                for l in syn.lemmas():
                    if l.name().lower() not in synonyms:
                        synonyms.append(l.name().lower())
                    if l.antonyms():
                        for ant in l.antonyms():
                            if ant.name().lower() not in antonyms:
                                antonyms.append(ant.name().lower())
            thesaurus_lines = [f"Thesaurus for '{word}' ({lang.title()}):"]
            if synonyms:
                thesaurus_lines.append(f"Synonyms: {', '.join(synonyms)}")
            else:
                thesaurus_lines.append("No synonyms found.")
            if antonyms:
                thesaurus_lines.append(f"Antonyms: {', '.join(antonyms)}")
            else:
                thesaurus_lines.append("No antonyms found.")
            return '\n'.join(thesaurus_lines)
        # For other languages, use API word_choices if available
        elif hasattr(self, 'last_word_choices') and self.last_word_choices:
            synonyms = [w['word'] for w in self.last_word_choices if w.get('word')]
            thesaurus_lines = [f"Thesaurus for '{word}' ({lang.title()}):"]
            if synonyms:
                thesaurus_lines.append(f"Synonyms: {', '.join(synonyms)}")
            else:
                thesaurus_lines.append("No synonyms found.")
            thesaurus_lines.append("No antonyms found.")
            return '\n'.join(thesaurus_lines)
        else:
            return f"Thesaurus for '{word}' ({lang.title()}):\nNo synonyms found.\nNo antonyms found.\n(Thesaurus is only available for English or when supported by the translation API.)"
