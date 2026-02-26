import random
import os
import json
import re

# 定義萬能類型，用於欺騙 ComfyUI 的類型檢查系統
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

class AceStep15PromptGenerator:
    """
    ACE-Step v1.5 自然語言 Prompt 專業生成器 (外部 Wildcards 版，支援多語言)
    """
    
    # 取得當前腳本所在的目錄
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 多語言 wildcards 目錄對應
    LANG_DIRS = {
        "en": "lyrics_wildcards_en",
        "zh": "lyrics_wildcards_zh",
        "jp": "lyrics_wildcards_jp"
    }

    # --- 擴展後的自然語言語料庫 (保留了16種曲風的強大描述) ---
    GENRE_DATA = {
        "Pop_流行": {"bpm": (90, 128), "instruments": ["shiny synthesizers", "a catchy bass groove", "crisp electronic beats", "acoustic guitar strums", "lush vocal harmonies", "a bright piano melody"], "vibes": ["polished and commercial", "radio-friendly and catchy", "modern and sleek", "bouncy and vibrant"], "dynamics": ["flows smoothly with an infectious hook", "builds to a euphoric chorus", "keeps a steady, danceable groove"]},
        "RandB_節奏藍調": {"bpm": (60, 90), "instruments": ["smooth Rhodes piano", "a deep synth bass", "syncopated drum machine beats", "silky vocal runs", "subtle electric guitar licks"], "vibes": ["sensual and smooth", "soulful and deep", "intimate and groovy", "late-night and atmospheric"], "dynamics": ["glides effortlessly through lush chords", "builds emotional intensity in the bridge", "maintains a steady, head-nodding bounce"]},
        "Hip-Hop_嘻哈": {"bpm": (80, 100), "instruments": ["a heavy boom-bap drum break", "a deep sub bass", "vinyl-sampled piano loops", "scratching elements", "punchy kick drums"], "vibes": ["gritty and street-smart", "classic and nostalgic", "heavy and rhythmic", "swagger-filled and confident"], "dynamics": ["rides a relentless drum pocket", "switches up the sample in the hook", "keeps a consistent, head-bobbing groove"]},
        "Trap_陷阱音樂": {"bpm": (130, 150), "instruments": ["rattling hi-hat rolls", "a massive 808 bass", "dark synth bells", "snappy snare drums", "pitch-bent brass"], "vibes": ["dark and menacing", "bouncy and aggressive", "modern and club-ready", "heavy and hypnotic"], "dynamics": ["drops hard into a bass-heavy chorus", "maintains tension with sparse verses", "hits with relentless percussive energy"]},
        "EDM_電子舞曲": {"bpm": (120, 130), "instruments": ["massive supersaw synths", "a four-on-the-floor kick drum", "sidechained basslines", "bright arpeggios", "risers and impacts"], "vibes": ["festival-ready and huge", "energetic and euphoric", "pumping and relentless", "neon-lit and vibrant"], "dynamics": ["builds up tension to a massive drop", "drives forward with undeniable energy", "explodes into a wall of synthetic sound"]},
        "House_浩室音樂": {"bpm": (118, 128), "instruments": ["a classic 909 drum kit", "a funky bassline", "stab chords", "soulful vocal chops", "shuffling hi-hats"], "vibes": ["groovy and uplifting", "deep and hypnotic", "club-focused and steady", "warm and rhythmic"], "dynamics": ["keeps the dancefloor moving consistently", "layers elements gradually over time", "drops into a satisfying, stripped-back bass groove"]},
        "Techno_電子樂": {"bpm": (125, 140), "instruments": ["a pounding, distorted kick drum", "industrial percussion", "a dark, rolling bassline", "hypnotic synth sequences", "white noise sweeps"], "vibes": ["dark and underground", "mechanical and relentless", "hypnotic and driving", "warehouse-ready and raw"], "dynamics": ["evolves slowly over a repetitive loop", "builds hypnotic tension", "pulses with unyielding industrial energy"]},
        "Drum_Bass_鼓打貝斯": {"bpm": (170, 178), "instruments": ["fast, complex breakbeats", "a roaring Reese bass", "atmospheric pads", "pitch-shifted vocal samples", "rapid-fire percussion"], "vibes": ["fast-paced and kinetic", "liquid and smooth", "heavy and aggressive", "futuristic and intense"], "dynamics": ["rushes forward with breakneck speed", "drops into a chaotic bass assault", "balances serene atmospheres with frantic drums"]},
        "Lo-Fi_低保真音樂": {"bpm": (70, 90), "instruments": ["dusty vinyl crackles", "a slightly detuned electric piano", "a sluggish, muffled drum beat", "warm upright bass", "subtle nature soundscapes"], "vibes": ["nostalgic and cozy", "relaxed and study-focused", "warm and analog", "chill and peaceful"], "dynamics": ["loops gracefully without ever peaking", "creates a comforting background texture", "drifts lazily through jazzy chords"]},
        "Jazz_爵士樂": {"bpm": (80, 120), "instruments": ["a breathy tenor saxophone", "a walking upright bass", "brushed snare drums", "improvisational grand piano", "a clean hollow-body guitar"], "vibes": ["sophisticated and smooth", "smoky and late-night", "swinging and lively", "elegant and timeless"], "dynamics": ["ebbs and flows with conversational solos", "swings effortlessly with the rhythm section", "breathes naturally through dynamic interplay"]},
        "Rock_搖滾樂": {"bpm": (110, 150), "instruments": ["distorted electric guitars", "punchy live drums", "a strong bassline", "power chords", "crash cymbals"], "vibes": ["raw and rebellious", "gritty and authentic", "stadium-filling", "hard-hitting"], "dynamics": ["builds dynamically from tension to explosion", "maintains a driving, relentless rhythm", "features explosive choruses and quiet verses"]},
        "Metal_金屬樂": {"bpm": (140, 200), "instruments": ["down-tuned, heavily distorted guitars", "rapid double-kick drums", "a clanking bass guitar", "aggressive blast beats", "screaming pinch harmonics"], "vibes": ["brutal and aggressive", "dark and intense", "heavy and unforgiving", "epic and face-melting"], "dynamics": ["crushes with a wall of heavy distortion", "switches from blistering speed to a heavy breakdown", "pummels the listener with unrelenting force"]},
        "Ambient_氛圍音樂": {"bpm": (40, 70), "instruments": ["swirling granular pads", "deep drone textures", "ethereal reverb sweeps", "minimalist synth bells"], "vibes": ["spacious and meditative", "formless and atmospheric", "ethereal", "tranquil"], "dynamics": ["drifts slowly without a clear melody", "evolves through subtle timbral shifts", "creates a vast sonic landscape"]},
        "Synthwave_合成器浪潮": {"bpm": (90, 110), "instruments": ["retro analog synthesizers", "a gated snare drum", "a driving 16th-note bassline", "neon-drenched arpeggiators", "electronic tom fills"], "vibes": ["nostalgic and 80s-inspired", "cyberpunk and neon-lit", "cinematic and retro-futuristic", "driving and synthetic"], "dynamics": ["cruises along a steady, retro groove", "builds dramatic tension with synth sweeps", "pulses with neon energy"]},
        "Cinematic_電影配樂": {"bpm": (60, 100), "instruments": ["sweeping string sections", "booming orchestral percussion", "a lonely solo piano", "deep brass swells", "a subtle choir"], "vibes": ["epic and larger-than-life", "intimate and breathtaking", "vast and atmospheric", "dramatic and emotional"], "dynamics": ["slowly swells into a grand crescendo", "ebbs and flows like a tide", "creates a building sense of awe"]},
        "Cinematic_Orchestral_管弦樂電影配樂": {"bpm": (70, 140), "instruments": ["soaring violins", "powerful brass sections", "thunderous cinematic percussion", "tremolo strings", "staccato cellos"], "vibes": ["epic and grand", "heroic", "intense and dramatic", "monumental"], "dynamics": ["builds into a massive orchestral swell", "features dramatic pauses and explosive crescendos", "commands attention with majestic scale"]},
        "Cyberpunk_賽博朋克": {"bpm": (90, 115), "instruments": ["distorted saw bass", "aggressive FM synths", "mechanical industrial beats", "glitchy electronic SFX"], "vibes": ["gritty and dystopian", "high-tech and dark", "neon-lit", "rebellious"], "dynamics": ["drives with a relentless mechanical pulse", "cuts through with sharp digital distortion", "pulsates with futuristic energy"]},
        "Celtic_凱爾特音樂": {"bpm": (80, 120), "instruments": ["uilleann pipes", "tin whistle", "celtic harp", "acoustic fiddle", "bodhran drum"], "vibes": ["mystical and ancient", "folksy", "whimsical", "spirited"], "dynamics": ["dances with a traditional rhythmic lilt", "soars with melodic folk lines", "evokes misty highlands and ancient legends"]},
        "Traditional_Chinese_中國傳統音樂": {"bpm": (60, 95), "instruments": ["plucked guzheng", "soulful erhu melody", "bamboo dizi flute", "pipa tremolo", "traditional yangqin"], "vibes": ["elegant and poetic", "zen-like", "oriental", "graceful"], "dynamics": ["flows like ink on paper with expressive vibrato", "paints a serene landscape with delicate plucking", "captures the essence of traditional beauty"]},
        "Bossa_Nova_波薩諾瓦": {"bpm": (80, 110), "instruments": ["nylon-string guitar chords", "soft jazz piano", "whispering shaker", "muted bassline", "gentle rimshots"], "vibes": ["breezy and sophisticated", "relaxed", "tropical", "smooth"], "dynamics": ["sways with a syncopated latin groove", "flows with effortless jazz elegance", "creates a sun-drenched, laid-back atmosphere"]},
        "Afrobeats_非洲節奏": {"bpm": (100, 125), "instruments": ["complex polyrhythmic percussion", "melodic synth leads", "heavy sub-bass", "shuffling hi-hats", "bright guitar riffs"], "vibes": ["infectious and danceable", "vibrant", "energetic", "celebratory"], "dynamics": ["grooves with a rich polyrhythmic drive", "pulses with rhythmic complexity", "invites constant movement and high energy"]},
        "ASMR_聽覺感官音樂": {"bpm": (40, 60), "instruments": ["soft whispers", "delicate finger tapping", "crinkling textures", "gentle brushing sounds", "close-mic breathing"], "vibes": ["intimate and tingly", "ultra-quiet", "sensory", "soothing"], "dynamics": ["focuses on micro-sounds and textures", "moves with extreme subtlety and closeness", "creates a deeply immersive sensory experience"]},
        "Reggae_雷鬼樂": {"bpm": (70, 90), "instruments": ["upstroke skank guitars", "a deep, dubby bassline", "a one-drop drum beat", "bright brass stabs", "a Hammond organ"], "vibes": ["sunny and relaxed", "positive and uplifting", "laid-back and island-inspired", "groovy and spiritual"], "dynamics": ["bounces with a steady, off-beat rhythm", "marches smoothly with heavy bass", "keeps a relaxed but steady groove"]},
        "Aboriginal_Australian_澳洲原住民音樂": {"bpm": (70, 110), "instruments": ["resonant didgeridoo drones", "clap sticks", "rhythmic vocal chanting", "hand percussion", "ancient flute melodies"], "vibes": ["ancient and spiritual", "earthy and primal", "ceremonial and meditative", "deeply rooted in the land"], "dynamics": ["pulses with a deep, droning resonance", "weaves chanting over hypnotic rhythm", "evokes the vast Australian outback"]},
        "Andean_安第斯音樂": {"bpm": (75, 110), "instruments": ["breathy pan flute melody", "charangos strumming", "bombo drum", "quena flute", "guitar arpeggios"], "vibes": ["majestic and mountainous", "mystical and ancient", "folkloric and warm", "soaring and open"], "dynamics": ["soars over high-altitude rhythms", "blends indigenous melody with Andean folk energy", "evokes misty mountain landscapes"]},
        "Anime_動漫音樂": {"bpm": (100, 145), "instruments": ["bright orchestral strings", "soaring synth leads", "energetic electric guitar", "driving drum kit", "shimmering piano arpeggios"], "vibes": ["passionate and youthful", "adventurous and emotional", "dramatic and inspiring", "vibrant and expressive"], "dynamics": ["bursts into an anthemic chorus with full instrumentation", "builds emotional intensity through layered strings", "captures the spirit of friendship and determination"]},
        "Balkan_巴爾幹音樂": {"bpm": (95, 160), "instruments": ["wild brass trumpet leads", "accordion swells", "clarinet runs", "tupan drum", "fast fiddle lines"], "vibes": ["wild and festive", "chaotic and joyful", "passionate and raw", "energetic and celebratory"], "dynamics": ["explodes with frenzied polyrhythmic energy", "charges forward with unruly brass fanfare", "whirls in a dizzying dance frenzy"]},
        "Chiptune_晶片音樂": {"bpm": (120, 160), "instruments": ["8-bit square wave melody", "triangle bass", "noise channel drums", "arpeggio pulses", "retro game sound effects"], "vibes": ["nostalgic and playful", "retro and pixelated", "quirky and upbeat", "nerdy and charming"], "dynamics": ["bounces with blocky electronic energy", "layers chiptone arpeggios into catchy hooks", "pulses with the heart of a classic video game"]},
        "Cumbia_昆比亞音樂": {"bpm": (95, 115), "instruments": ["marimba melody", "caja drum pattern", "guacharaca scraper", "accordion riffs", "bass guitar groove"], "vibes": ["infectious and danceable", "tropical and festive", "warm and communal", "rhythmic and joyful"], "dynamics": ["grooves with an irresistible syncopated Cumbia beat", "flows with Latin tropical warmth", "keeps dancers moving with steady rhythmic energy"]},
        "Epic_Trailer_史詩預告音樂": {"bpm": (55, 100), "instruments": ["massive orchestral brass hits", "thundering taiko drums", "sweeping string risers", "deep bass impacts", "powerful choir stabs"], "vibes": ["earth-shattering and bombastic", "cinematic and intense", "heroic and climactic", "awe-inspiring and monumental"], "dynamics": ["slams into a colossal climax with every element at full force", "builds relentless tension through percussion and brass", "delivers maximum impact with layered hits and swells"]},
        "Flamenco_弗拉明戈音樂": {"bpm": (100, 160), "instruments": ["rapid flamenco guitar picado runs", "percussive palmas clapping", "cajon drum", "passionate female vocals", "zapateado footstep rhythms"], "vibes": ["passionate and fierce", "raw and emotional", "elegant and proud", "intense and dramatic"], "dynamics": ["ignites with furious guitar strumming and foot stomps", "flows between deep emotional lament and explosive energy", "commands the stage with Spanish fire and grace"]},
        "Flamenco_Fusion_弗拉明戈融合音樂": {"bpm": (90, 130), "instruments": ["electric flamenco guitar", "cajon and drum kit hybrid", "jazz bass", "subtle synth pads", "violin flourishes"], "vibes": ["bold and contemporary", "passionate yet modern", "cinematic and expressive", "cross-cultural and innovative"], "dynamics": ["blends flamenco fire with modern grooves", "fuses acoustic tradition with electronic textures", "bridges Spanish classical roots with global influences"]},
        "Gamelan_加麥蘭音樂": {"bpm": (50, 80), "instruments": ["bronze gong ageng strikes", "metallic gangsa patterns", "kendang drum pulse", "suling flute tones", "resonant saron melody"], "vibes": ["meditative and hypnotic", "ceremonial and mystical", "ancient and ornate", "interlocking and cyclical"], "dynamics": ["layers interlocking metallic patterns into a shimmering whole", "pulses through long cyclic gong structures", "creates a trance-like ceremonial atmosphere"]},
        "Gospel_福音音樂": {"bpm": (70, 110), "instruments": ["powerful gospel choir", "Hammond B3 organ", "grand piano chords", "tambourine", "electric bass and live drums"], "vibes": ["uplifting and soulful", "spiritual and powerful", "joyful and communal", "deeply emotional and sincere"], "dynamics": ["rises to an ecstatic call-and-response climax", "builds from quiet devotion to full congregational glory", "fills the room with warmth and divine energy"]},
        "Greek_Folk_希臘民謠": {"bpm": (85, 130), "instruments": ["bouzouki melody", "baglamas strumming", "lyra fiddle", "daouli drum", "clarinet lines"], "vibes": ["spirited and communal", "nostalgic and Mediterranean", "festive and passionate", "earthy and traditional"], "dynamics": ["dances with zeimbekiko swagger and soulful melody", "builds into a lively circle dance celebration", "carries the warmth of a Greek taverna"]},
        "Hawaiian_夏威夷音樂": {"bpm": (65, 95), "instruments": ["slack-key guitar picking", "steel guitar glides", "ukulele strums", "light percussion", "soft vocal harmonies"], "vibes": ["breezy and tropical", "gentle and serene", "warm and nostalgic", "island-spirited and joyful"], "dynamics": ["glides with the ease of ocean waves", "blooms with gentle melodic warmth", "captures the peaceful spirit of the islands"]},
        "JRPG_日式角色扮演遊戲": {"bpm": (75, 120), "instruments": ["emotive piano melody", "sweeping orchestral strings", "light chiptune accents", "harp arpeggios", "gentle choir"], "vibes": ["adventurous and heartfelt", "nostalgic and magical", "epic yet intimate", "fantasy-driven and emotional"], "dynamics": ["unfolds like a chapter from an epic quest", "balances quiet wonder with soaring melodic peaks", "captures the emotional journey of a heros story"]},
        "JRPG_Battle_日式角色扮演遊戲戰鬥音樂": {"bpm": (140, 175), "instruments": ["driving electric guitar riffs", "thundering orchestral percussion", "fast bass lines", "synth brass fanfares", "aggressive string ostinatos"], "vibes": ["intense and heroic", "fast-paced and adrenaline-fueled", "triumphant and fierce", "dramatic and urgent"], "dynamics": ["charges into battle with relentless tempo and force", "escalates tension through rapid rhythmic layering", "delivers non-stop energy and decisive power"]},
        "Mariachi_墨西哥流浪樂隊音樂": {"bpm": (95, 140), "instruments": ["bright trumpets in harmony", "vihuela strumming", "guitarron bass", "classical violin leads", "guitar chord stabs"], "vibes": ["festive and vibrant", "proud and passionate", "warm and celebratory", "bold and theatrical"], "dynamics": ["bursts with melodic brass fanfare and joyful rhythm", "alternates between tender ballad and rousing celebration", "fills the air with Mexican folk spirit"]},
        "Middle_Eastern_中東音樂": {"bpm": (70, 115), "instruments": ["oud improvisation", "darbuka drum patterns", "qanun strings", "ney flute phrases", "riq tambourine"], "vibes": ["ornate and mysterious", "sensual and ancient", "meditative and rich", "exotic and soulful"], "dynamics": ["weaves sinuous melodic lines over complex rhythmic cycles", "builds with maqam-based ornamentation and passion", "transports the listener through ancient bazaars and desert nights"]},
        "Mongolian_蒙古音樂": {"bpm": (65, 105), "instruments": ["morin khuur horse-head fiddle", "throat singing (khoomei)", "Mongolian flute", "shanz lute", "frame drum"], "vibes": ["vast and nomadic", "powerful and primal", "ancient and spiritual", "sweeping and rugged"], "dynamics": ["echoes across endless steppes with overtone chanting", "surges with equestrian energy and raw melodic force", "evokes the boundless freedom of the Mongolian plains"]},
        "Native_American_美洲原住民音樂": {"bpm": (60, 100), "instruments": ["cedar flute melody", "frame drum heartbeat", "rattle percussion", "ceremonial chanting", "wind sounds"], "vibes": ["sacred and deeply rooted", "meditative and earthy", "spiritual and serene", "ancient and natural"], "dynamics": ["breathes with the rhythm of the land", "rises in ceremonial chant and then fades to silence", "honors the natural world with reverent, cyclical patterns"]},
        "Nordic_Folk_北歐民謠": {"bpm": (80, 120), "instruments": ["nyckelharpa melody", "hardanger fiddle", "wooden flute", "drone string pads", "hand drum"], "vibes": ["mystical and cold", "ancient and runic", "melancholic and beautiful", "folklore-driven and wild"], "dynamics": ["sweeps with the wind of Norse mythology", "dances with melancholy grace and Nordic pride", "evokes frost-covered forests and Viking sagas"]},
        "Persian_Classical_波斯古典音樂": {"bpm": (50, 90), "instruments": ["tar lute improvisation", "santur hammered dulcimer", "tombak drum patterns", "ney flute ornaments", "setar delicate plucking"], "vibes": ["poetic and refined", "deeply expressive", "ancient and meditative", "ornate and passionate"], "dynamics": ["unfolds through complex dastgah modes with expressive freedom", "breathes with Persian poetic sensibility", "moves from silent introspection to ecstatic ornamentation"]},
        "Samba_森巴": {"bpm": (90, 110), "instruments": ["surdo bass drum", "tamborim high percussion", "cuica friction drum", "cavaquinho strumming", "ganza shaker"], "vibes": ["explosive and joyful", "carnival-ready and electric", "rhythmically complex and festive", "vibrant and passionate"], "dynamics": ["ignites with the unstoppable energy of Rio Carnival", "layers percussion into a thunderous polyrhythmic celebration", "drives forward with infectious samba swing"]},
        "Scandinavian_Folk_斯堪的納維亞民謠": {"bpm": (75, 115), "instruments": ["fiddle folk melody", "accordion drone", "cittern strumming", "wooden recorder", "jaw harp"], "vibes": ["rustic and pastoral", "cozy and introspective", "ancient yet familiar", "earthy and communal"], "dynamics": ["dances with simple, heartfelt folk charm", "rings with the clarity of Northern European tradition", "creates a warm fireside atmosphere through acoustic simplicity"]},
        "Tango_探戈": {"bpm": (60, 90), "instruments": ["bandoneon swells", "staccato violin stabs", "double bass walking line", "piano rhythmic comping", "dramatic pauses"], "vibes": ["passionate and sensual", "tense and dramatic", "elegant and dangerous", "melancholic and fiery"], "dynamics": ["surges with explosive passion followed by sudden silence", "entwines instruments in a dramatic musical dialogue", "commands the floor with pride, precision, and deep emotion"]},
        "Turkish_Folk_土耳其民謠": {"bpm": (80, 130), "instruments": ["saz baglama melody", "davul drum", "zurna shawm", "ney flute", "def frame drum"], "vibes": ["vibrant and regional", "passionate and folkloric", "ancient and soulful", "spirited and communal"], "dynamics": ["charges with Anatolian rhythmic fire and folk pride", "weaves ornamented melodic lines over driving percussion", "carries the cultural richness of Turkeys diverse heritage"]}    }

    MOOD_DATA = {

        # ========== 原有8種（中英文key修正版）==========

        "Happy_快樂": {"scale": "Major", "adjs": ["uplifting", "joyful", "bright", "positive", "feel-good", "cheerful"], "balances": ["joy and sunshine", "energy and smiles", "positivity and light"]},
        "Sad_悲傷": {"scale": "Minor", "adjs": ["melancholic", "heartbreaking", "sorrowful", "tear-jerking", "emotional"], "balances": ["sorrow and reflection", "pain and beauty", "loss and longing"]},
        "Energetic_活力": {"scale": "Major", "adjs": ["powerful", "high-energy", "driving", "adrenaline-fueled", "intense"], "balances": ["aggression and excitement", "power and rhythm", "motion and force"]},
        "Relaxed_放鬆": {"scale": "Major", "adjs": ["soothing", "laid-back", "chill", "calm", "mellow"], "balances": ["calm and warmth", "peace and tranquility", "ease and comfort"]},
        "Dark_黑暗": {"scale": "Minor", "adjs": ["ominous", "scary", "mysterious", "shadowy", "creepy"], "balances": ["tension and fear", "mystery and gloom", "suspense and dread"]},
        "Romantic_浪漫": {"scale": "Minor", "adjs": ["intimate", "passionate", "sentimental", "tender", "warm"], "balances": ["love and desire", "sweetness and longing", "affection and warmth"]},
        "Epic_史詩": {"scale": "Minor", "adjs": ["grand", "heroic", "legendary", "vast", "triumphant"], "balances": ["glory and scale", "power and majesty", "myth and might"]},
        "Dreamy_夢幻": {"scale": "Major", "adjs": ["surreal", "soft", "floating", "ethereal", "hypnotic"], "balances": ["fantasy and reality", "clouds and stardust", "sleep and imagination"]},

        # ========== 新增情緒類（8種）==========

        "Angry_憤怒": {"scale": "Minor", "adjs": ["furious", "aggressive", "raw", "explosive", "fierce"], "balances": ["rage and release", "power and destruction", "tension and violence"]},
        "Melancholic_惆悵": {"scale": "Minor", "adjs": ["wistful", "bittersweet", "pensive", "quietly sad", "reflective"], "balances": ["memory and loss", "sweetness and ache", "past and longing"]},
        "Hopeful_希望": {"scale": "Major", "adjs": ["warm", "tender", "optimistic", "gentle", "rising"], "balances": ["light and possibility", "faith and courage", "dawn and new beginnings"]},
        "Lonely_孤獨": {"scale": "Minor", "adjs": ["isolated", "hollow", "quiet", "distant", "empty"], "balances": ["silence and longing", "absence and memory", "solitude and stillness"]},
        "Nostalgic_懷舊": {"scale": "Major", "adjs": ["bittersweet", "warm", "hazy", "reminiscent", "tender"], "balances": ["past and present", "memory and warmth", "time and longing"]},
        "Euphoric_狂喜": {"scale": "Major", "adjs": ["overwhelming", "ecstatic", "soaring", "electric", "transcendent"], "balances": ["release and joy", "abandon and bliss", "peak and infinity"]},
        "Anxious_緊張": {"scale": "Minor", "adjs": ["uneasy", "tense", "restless", "unsettled", "nerve-wracking"], "balances": ["unease and dread", "anticipation and fear", "pressure and uncertainty"]},
        "Triumphant_勝利": {"scale": "Major", "adjs": ["victorious", "resolute", "proud", "powerful", "soaring"], "balances": ["struggle and victory", "effort and reward", "perseverance and glory"]},

        # ========== 新增氛圍/環境類（6種）==========

        "Mystical_神秘": {"scale": "Minor", "adjs": ["enigmatic", "otherworldly", "arcane", "hazy", "spellbinding"], "balances": ["magic and shadow", "the known and unknown", "wonder and mystery"]},
        "Spiritual_靈性": {"scale": "Major", "adjs": ["sacred", "devotional", "transcendent", "reverent", "pure"], "balances": ["earth and heaven", "silence and grace", "soul and light"]},
        "Playful_俏皮": {"scale": "Major", "adjs": ["quirky", "bouncy", "light-hearted", "cheeky", "fun"], "balances": ["humor and energy", "innocence and mischief", "play and laughter"]},
        "Suspenseful_懸疑": {"scale": "Minor", "adjs": ["tense", "cinematic", "foreboding", "thrilling", "gripping"], "balances": ["danger and silence", "the seen and unseen", "threat and anticipation"]},
        "Wilderness_曠野": {"scale": "Major", "adjs": ["vast", "primal", "untamed", "expansive", "raw"], "balances": ["nature and solitude", "freedom and earth", "wind and distance"]},
        "Urban_都市": {"scale": "Minor", "adjs": ["gritty", "street-smart", "raw", "sharp", "contemporary"], "balances": ["concrete and neon", "hustle and survival", "noise and ambition"]}

    }

    ROOT_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # --- 防呆備用庫 (當找不到 JSON 檔案時使用) ---
    FALLBACK_THEMES = {
        "Love": {"lines": ["Looking into your eyes", "Heart beating fast tonight"], "phrase": "Love is all we need"},
        "City": {"lines": ["Neon lights flickering by", "Concrete jungle beneath the sky"], "phrase": "City never sleeps"},
        "Space": {"lines": ["Stars drifting past the glass", "Universe moving way too fast"], "phrase": "Gravity lets go"}
    }
    FALLBACK_TEMPLATES = {
        "Standard": "[Intro]\n(Instrumental)\n\n[Verse 1]\n{theme_line_1}\n{theme_line_2}\nWaiting for the moment to arise\n\n[Chorus]\n{power_phrase}!\nLet the rhythm take control\n\n[Outro]\nFading out..."
    }

    PROMPT_TEMPLATE = (
        "A {adj_1}, {adj_2} modern {genre} track with a {vibe} edge. "
        "Driven by {inst_1}, {inst_2}, and {inst_3}. "
        "The song {dynamic}, balancing {balance}."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "genre": (["Random"] + list(cls.GENRE_DATA.keys()), {"default": "Random"}),
                "mood": (["Random"] + list(cls.MOOD_DATA.keys()), {"default": "Random"}),
                "vocal_mode": (["Full Lyrics", "Instrumental", "Choir/Humming"], {"default": "Full Lyrics"}),
                "language": (["en", "zh", "jp"], {"default": "en", "tooltip": "選擇歌詞語言"}),  # 新增語言選單
            },
            "optional": {
                "extra_prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "手動補充的 Prompt"}),
            }
        }

    # 修改 RETURN_TYPES 和 RETURN_NAMES，增加 language 輸出
    RETURN_TYPES = ("STRING", "STRING", "INT", AnyType("*"), AnyType("*"), "STRING", "STRING" )
    RETURN_NAMES = ("prompt", "lyrics", "bpm", "keyscale", "language", "genre", "mood")
    FUNCTION = "generate_ace_params"
    CATEGORY = "AI Music/ACE-Step"

    def generate_ace_params(self, seed, genre, mood, vocal_mode, language, extra_prompt=""):
        rng = random.Random(seed) if seed > 0 else random.Random()
            
        selected_genre = genre if genre != "Random" else rng.choice(list(self.GENRE_DATA.keys()))
        genre_info = self.GENRE_DATA[selected_genre]
        bpm = rng.randint(genre_info["bpm"][0], genre_info["bpm"][1])
        
        selected_mood = mood if mood != "Random" else rng.choice(list(self.MOOD_DATA.keys()))
        mood_info = self.MOOD_DATA[selected_mood]
        root = rng.choice(self.ROOT_NOTES)
        keyscale = f"{root} {mood_info['scale']}"

        # --- 1. 生成自然語言 Prompt ---
        adjs = rng.sample(mood_info["adjs"], 2)
        insts = rng.sample(genre_info["instruments"], min(3, len(genre_info["instruments"])))
        vibe = rng.choice(genre_info["vibes"])
        dynamic = rng.choice(genre_info["dynamics"])
        balance = rng.choice(mood_info["balances"])

        final_prompt = self.PROMPT_TEMPLATE.format(
            adj_1=adjs[0], adj_2=adjs[1], genre=selected_genre.lower(), vibe=vibe,
            inst_1=insts[0], inst_2=insts[1], inst_3=insts[2], dynamic=dynamic, balance=balance
        )
        
        if extra_prompt and extra_prompt.strip():
            final_prompt = f"{final_prompt} {extra_prompt.strip()}"

        # --- 2. 生成歌詞 (根據 Vocal Mode 和語言) ---
        final_lyrics = ""

        if vocal_mode == "Instrumental":
            final_lyrics = "[Instrumental]"
            
        elif vocal_mode == "Choir/Humming":
            # 內建的簡單人聲模式（可以根據語言調整提示文字）
            if language == "en":
                final_lyrics = "[Intro]\n(Epic Choir vocalizing...)\n\n[Verse]\n(Soft humming)\n\n[Chorus]\n(Powerful Choir singing Ahhh and Ohhh)\n\n[Outro]\n(Fading vocalizing)"
            elif language == "zh":
                final_lyrics = "[前奏]\n(史詩合唱人聲...)\n\n[主歌]\n(輕柔哼唱)\n\n[副歌]\n(強力合唱唱出啊啊和喔喔)\n\n[尾奏]\n(人聲漸弱)"
            elif language == "jp":
                final_lyrics = "[イントロ]\n(壮大な合唱ボーカル...)\n\n[バース]\n(優しいハミング)\n\n[コーラス]\n(力強い合唱でアーとオー)\n\n[アウトロ]\n(ボーカルフェードアウト)"
            
        elif vocal_mode == "Full Lyrics":
            # 根據選擇的語言決定要讀取的目錄
            lang_dir_name = self.LANG_DIRS.get(language, "lyrics_wildcards_en")
            wildcards_dir = os.path.join(self.BASE_DIR, lang_dir_name)
            
            # 只取 key 的英文部分作為 JSON 檔名，例如 "Rock_搖滾樂" -> "rock.json"
            json_genre_name = selected_genre.encode("ascii", errors="ignore").decode().rstrip("_").lower().strip()
            json_file_path = os.path.join(wildcards_dir, f"{json_genre_name}.json")
            
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    wildcards_data = json.load(f)
                
                # 從 JSON 中抽取一個骨架
                structure = rng.choice(wildcards_data.get("structures", ["[Verse]\n{verse}\n\n[Chorus]\n{chorus}"]))
                
                # 動態替換 {tag}。使用正則表達式，確保每次遇到 {verse} 時都會重新抽取一次隨機句子
                def replace_tag(match):
                    tag_name = match.group(1)
                    if tag_name in wildcards_data and isinstance(wildcards_data[tag_name], list) and wildcards_data[tag_name]:
                        picked = rng.choice(wildcards_data[tag_name])
                        # 防呆機制：如果抽到的東西還是陣列 (list)，就取出它的第一筆轉成字串
                        if isinstance(picked, list):
                            return str(picked[0]) if picked else ""
                        return str(picked)
                    return match.group(0) # 如果找不到對應的標籤庫，保持原樣
                
                final_lyrics = re.sub(r'\{([^}]+)\}', replace_tag, structure)
                
            except (FileNotFoundError, json.JSONDecodeError) as e:
                # 防呆機制：如果找不到 JSON 檔案，或是 JSON 格式寫錯，退回使用內建備用庫
                print(f"[ACE-Step Generator] Warning: 無法讀取 {json_genre_name}.json in {lang_dir_name} ({e})。正在使用備用歌詞庫。")
                theme_data = rng.choice(list(self.FALLBACK_THEMES.values()))
                final_lyrics = self.FALLBACK_TEMPLATES["Standard"].format(
                    theme_line_1=theme_data["lines"][0],
                    theme_line_2=theme_data["lines"][1],
                    power_phrase=theme_data["phrase"]
                )

        # 返回參數中增加 language
        return (final_prompt, final_lyrics, bpm, keyscale, language, genre, mood)

# 節點註冊
NODE_CLASS_MAPPINGS = {
    "AceStep15PromptGenerator": AceStep15PromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceStep15PromptGenerator": "🎹 ACE-Step 1.5 Auto-Producer (Multi-language)"
}