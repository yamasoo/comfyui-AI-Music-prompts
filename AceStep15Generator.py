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

    # --- 擴展後的自然語言語料庫 ---
    GENRE_DATA = {
        "Pop_流行": {"bpm": (90, 128), "instruments": ["shiny synthesizers", "a catchy bass groove", "crisp electronic beats", "acoustic guitar strums", "lush vocal harmonies", "a bright piano melody"], "vibes": ["polished and commercial", "radio-friendly and catchy", "modern and sleek", "bouncy and vibrant"], "dynamics": ["flows smoothly with an infectious hook", "builds to a euphoric chorus", "keeps a steady, danceable groove"]},
        "K-Pop_韓流": {"bpm": (95, 140), "instruments": ["punchy EDM synths", "tight trap hi-hats", "melodic vocal chops", "orchestral string hits", "bass-heavy drops"], "vibes": ["polished and high-energy", "synchronized and flashy", "youthful and addictive", "futuristic and sleek"], "dynamics": ["explodes into a perfectly engineered hook", "transitions sharply between rap verses and soaring choruses", "maintains relentless idol-group intensity"]},
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
        "Scottish_Folk_蘇格蘭風格": {"bpm": (80, 130), "instruments": ["Great Highland bagpipe", "snare drum march", "bass drum", "tenor drum swings", "massed pipe band drones"], "vibes": ["proud and martial", "windswept and majestic", "ceremonial and stirring", "ancient and clan-spirited"], "dynamics": ["marches with military precision and grandeur", "swells into a full pipe band wall of sound", "stirs deep ancestral pride with every drone"]},
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
        "LOGH_EDStyle_銀英ED風格": {"bpm": (70, 85), "instruments": ["weathered yet warm narrative male vocals", "Opera bass old male vocals", "deep introspective orchestral strings", "restrained melancholic piano", "sparse classical guitar", "solemn brass ensemble"], "vibes": ["epic and introspective", "melancholic yet hopeful", "historically weighty", "nostalgic and reverent", "serene but powerful"], "dynamics": ["verses are intimate with sparse piano and soft strings supporting the vocal narrative", "chorus gradually swells with full strings and brass creating a vast tribute-like atmosphere", "overall progression feels like a slowly unfolding space elegy rather than explosive energy bursts"]},
        "Enka_演歌": {"bpm": (50, 75), "instruments": ["tremolo electric guitar", "soaring strings", "shakuhachi flute", "taiko accents", "lush orchestral brass"], "vibes": ["melancholic and nostalgic", "stoic and soulful", "bittersweet and lonely", "dramatic and resilient"], "dynamics": ["slow-burning emotional build-ups", "expressive vocal-like vibrato on lead instruments", "cycles of heavy sorrow followed by dignified resolve"]},
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


    # 擴展後的 Prompt 範本庫 (對應下拉選單)
    PROMPT_TEMPLATES = {
        "Standard_標準": (
            "A {adj_1}, {adj_2} modern {genre} track with a {vibe} edge. "
            "Driven by {inst_1}, {inst_2}, and {inst_3}. "
            "The song {dynamic}, balancing {balance}."
        ),
        "Structured_結構化": (
            "{genre}, {vibe}, {bpm} bpm, {inst_1}, {inst_2}, {inst_3}, "
            "{adj_1}, {adj_2}, {mood} mood, high quality, clear production, masterpiece."
        ),
        "Groove_節奏律動": (
            "Heavy groove {genre} track at {bpm} bpm. Focus on rhythmic {inst_1} and punchy {inst_2}, "
            "layered with {inst_3}. The overall vibe is {vibe} and {adj_1}. {dynamic}."
        ),
        "Cinematic_電影敘事": (
            "Cinematic and emotional {genre} soundtrack, {mood} atmosphere. The scene opens with {inst_1}, "
            "gradually building up with {inst_2} and {inst_3}. "
            "Features {adj_1} and {adj_2} textures. {dynamic}."
        ),
        "Vintage_復古類比": (
            "Vintage {genre} style, {bpm} bpm. Analog warmth, {vibe} feel. "
            "Instrumentation includes {inst_1}, {inst_2}, and {inst_3}. "
            "Mood is {adj_1} and {adj_2}. {dynamic}."
        )
    }
    # --- 新增：人聲特徵標籤對應庫 ---
    VOCAL_TIMBRE_MAP = {
        "Female (Clear/Pop)": "featuring clear and bright female vocals",
        "Female (Husky/Soulful)": "featuring soulful, husky female vocals",
        "Female (Ethereal)": "featuring ethereal and breathy female vocals",
        "Male (Deep)": "featuring deep, resonant male vocals",
        "Male (High/Tenor)": "featuring soaring, high-pitched male vocals",
        "Male (Rough/Rock)": "featuring rough, gritty male vocals",
        "Choir": "featuring a powerful background choir",
        "Duet (Male & Female)": "featuring a male and female vocal duet"
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "genre": (["Random"] + list(cls.GENRE_DATA.keys()), {"default": "Random"}),
                "mood": (["Random"] + list(cls.MOOD_DATA.keys()), {"default": "Random"}),
                "vocal_mode": (["Random", "Full Lyrics", "All Lyrics", "Instrumental", "Choir/Humming"], {"default": "Full Lyrics"}),
                "language": (["Random", "en", "zh", "jp"], {"default": "en", "tooltip": "選擇歌詞語言（Random 會隨機抽選一種）"}),
                "prompt_style": (["Random", "Standard_標準", "Structured_結構化", "Groove_節奏律動", "Cinematic_電影敘事", "Vintage_復古類比"], {"default": "Random"}),
                "vocal_timbre": (["Random", "None"] + list(cls.VOCAL_TIMBRE_MAP.keys()), {"default": "Random", "tooltip": "指定歌手聲線特徵"}),
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

    
    # 👇 1. 這裡補上了 vocal_timbre 參數
    def generate_ace_params(self, seed, genre, mood, vocal_mode, language, prompt_style, vocal_timbre, extra_prompt=""):
        rng = random.Random(seed) if seed > 0 else random.Random()
            
        selected_genre = genre if genre != "Random" else rng.choice(list(self.GENRE_DATA.keys()))
        genre_info = self.GENRE_DATA[selected_genre]
        bpm = rng.randint(genre_info["bpm"][0], genre_info["bpm"][1])
        
        selected_mood = mood if mood != "Random" else rng.choice(list(self.MOOD_DATA.keys()))
        mood_info = self.MOOD_DATA[selected_mood]
        root = rng.choice(self.ROOT_NOTES)
        keyscale = f"{root} {mood_info['scale']}"

        # 處理 language Random 抽選
        language = language if language != "Random" else rng.choice(["en", "zh", "jp"])

        # 處理 vocal_mode Random 抽選
        if vocal_mode == "Random":
            vocal_mode = rng.choice(["Full Lyrics", "All Lyrics", "Instrumental", "Choir/Humming"])

        # 👇 2. 新增：處理人聲特徵 (防呆邏輯)
        actual_vocal_string = ""
        if vocal_mode == "Instrumental":
            actual_vocal_string = "pure instrumental, no vocals"
        else:
            # 如果是 Random 就從字典裡抽一個，如果是 None 就不加標籤
            chosen_timbre = vocal_timbre
            if chosen_timbre == "Random":
                chosen_timbre = rng.choice(list(self.VOCAL_TIMBRE_MAP.keys()))
            
            if chosen_timbre != "None" and chosen_timbre in self.VOCAL_TIMBRE_MAP:
                actual_vocal_string = self.VOCAL_TIMBRE_MAP[chosen_timbre]

        # --- 1. 生成多樣化 Prompt ---
        adjs = rng.sample(mood_info["adjs"], 2)
        insts = rng.sample(genre_info["instruments"], min(3, len(genre_info["instruments"])))
        vibe = rng.choice(genre_info["vibes"])
        dynamic = rng.choice(genre_info["dynamics"])
        balance = rng.choice(mood_info["balances"])

        # 根據選擇決定風格 (如果是 Random 就隨機抽一個)
        selected_style_key = prompt_style if prompt_style != "Random" else rng.choice(list(self.PROMPT_TEMPLATES.keys()))
        selected_template = self.PROMPT_TEMPLATES[selected_style_key]

        # 填入變數組成最終字串
        final_prompt = selected_template.format(
            adj_1=adjs[0], adj_2=adjs[1], 
            genre=selected_genre.split('_')[0].lower(), 
            vibe=vibe, bpm=bpm, mood=selected_mood.split('_')[0].lower(),
            inst_1=insts[0], inst_2=insts[1], inst_3=insts[2], 
            dynamic=dynamic, balance=balance
        )
        
        # 👇 3. 新增：將人聲特徵融合進 Prompt 中
        if actual_vocal_string:
            final_prompt = f"{final_prompt}, {actual_vocal_string}"

        # 如果有手寫的 extra_prompt 才加上去
        if extra_prompt and extra_prompt.strip():
            final_prompt = f"{final_prompt}, {extra_prompt.strip()}"
        
        
        # --- 2. 生成歌詞 (支援長時長生成的擴展結構版) ---
        final_lyrics = ""
        json_genre_name = selected_genre.encode("ascii", errors="ignore").decode().rstrip("_").lower().strip()

        if vocal_mode == "Instrumental":
            # 抓取前兩個樂器來做互動，讓音樂更有層次
            main_inst = insts[0].split()[-1].capitalize() if insts else "Instrument"
            second_inst = insts[1].split()[-1].capitalize() if len(insts) > 1 else "Rhythm section"
            
            # 完整的 10 段式長時長樂曲結構
            final_lyrics = (
                f"[Intro]\n(Atmospheric buildup, introducing the {main_inst})\n\n"
                f"[Verse 1]\n(Steady rhythm, melodic {main_inst} playing softly)\n\n"
                f"[Pre-Chorus]\n(Building tension, {second_inst} joins in)\n\n"
                f"[Chorus]\n(Full band instrumental, energetic and wide)\n\n"
                f"[Verse 2]\n(Rhythmic variation, deeper groove)\n\n"
                f"[Chorus]\n(Full band instrumental, driving force)\n\n"
                f"[Bridge]\n(Breakdown, quiet and emotional textures, stripping back the beat)\n\n"
                f"[Instrumental Solo]\n(Passionate {main_inst} solo!)\n\n"
                f"[Final Chorus]\n(Epic climax, all instruments playing at maximum energy)\n\n"
                f"[Outro]\n(Gradual fade out, lingering {main_inst} notes)"
            )
            
        elif vocal_mode == "Choir/Humming":
            # 擴充版無字人聲/合唱結構 (7~8段)，防止 AI 提早沒詞唱
            if language == "en":
                final_lyrics = (
                    "[Intro]\n(Ethereal vocalizing...)\n\n"
                    "[Verse 1]\n(Soft rhythmic humming: mmm...)\n\n"
                    "[Chorus]\n(Powerful Choir singing Ahhh, wordless)\n\n"
                    "[Verse 2]\n(Deep resonant humming, slowly building)\n\n"
                    "[Chorus]\n(Epic Choir singing Ohhh, maximum emotion)\n\n"
                    "[Bridge]\n(Solo haunting voice vocalizing smoothly)\n\n"
                    "[Final Chorus]\n(Massive Choir chanting Ahhh and Ohhh together!)\n\n"
                    "[Outro]\n(Fading breathy vocals... mmm...)"
                )
            elif language == "zh":
                final_lyrics = (
                    "[前奏]\n(空靈的無字吟唱...)\n\n"
                    "[主歌 1]\n(輕柔的節奏哼唱：嗯...)\n\n"
                    "[副歌]\n(氣勢磅礴的合唱 啊，無歌詞)\n\n"
                    "[主歌 2]\n(低沉的共鳴哼唱，情緒逐漸堆疊)\n\n"
                    "[副歌]\n(史詩級合唱 喔，情感釋放)\n\n"
                    "[橋段]\n(單一聲線的幽美吟唱，穿透力強)\n\n"
                    "[最後副歌]\n(全體大合唱 啊與喔，推向最高潮！)\n\n"
                    "[尾奏]\n(氣音漸弱... 嗯...)"
                )
            elif language == "jp":
                final_lyrics = (
                    "[イントロ]\n(幻想的なスキャット...)\n\n"
                    "[バース 1]\n(優しいハミング：んー...)\n\n"
                    "[コーラス]\n(力強い合唱 アー、歌詞なし)\n\n"
                    "[バース 2]\n(深みのあるハミング、徐々に盛り上がる)\n\n"
                    "[コーラス]\n(壮大な合唱 オー、感情の爆発)\n\n"
                    "[ブリッジ]\n(透き通るようなソロのボーカライズ)\n\n"
                    "[ラストコーラス]\n(大合唱でアーとオー、最高潮！)\n\n"
                    "[アウトロ]\n(息づかいのフェードアウト... んー...)"
                )
            
            
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
                
                # 1. 將整首歌按雙換行拆分為獨立區塊 (如 [Verse 1], [Chorus]...)
                sections = structure.split("\n\n")
                processed_sections = []

                for section in sections:
                    # 2. 為當前區塊建立獨立的抽樣池
                    section_pools = {}
                    
                    def replace_tag_block(match):
                        tag_name = match.group(1)
                        if tag_name in wildcards_data and isinstance(wildcards_data[tag_name], list) and wildcards_data[tag_name]:
                            
                            # 如果這個標籤在當前區塊還沒建立抽樣池，就建一個並打亂
                            if tag_name not in section_pools:
                                pool = list(wildcards_data[tag_name]) # 複製一份詞庫
                                rng.shuffle(pool)                     # 隨機打亂
                                section_pools[tag_name] = pool

                            # 如果池子抽乾了 (防呆: 區塊內需要的句子數量 > 詞庫總量)
                            if not section_pools[tag_name]:
                                pool = list(wildcards_data[tag_name])
                                rng.shuffle(pool)
                                section_pools[tag_name] = pool

                            # 3. 彈出一個詞 (保證當前池內不重複)
                            picked = section_pools[tag_name].pop()
                            
                            # 防呆機制：處理巢狀陣列情況
                            if isinstance(picked, list):
                                return str(picked[0]) if picked else ""
                            return str(picked)
                            
                        return match.group(0) # 如果找不到對應標籤，保持原樣

                    # 處理單個區塊
                    processed_section = re.sub(r'\{([^}]+)\}', replace_tag_block, section)
                    processed_sections.append(processed_section)
                
                # 4. 將處理完的區塊重新組裝成完整的歌詞
                final_lyrics = "\n\n".join(processed_sections)
                
            except (FileNotFoundError, json.JSONDecodeError) as e:
                # 防呆機制：如果找不到 JSON 檔案，或是 JSON 格式寫錯，退回使用內建備用庫
                print(f"[ACE-Step Generator] Warning: 無法讀取 {json_genre_name}.json in {lang_dir_name} ({e})。正在使用備用歌詞庫。")
                theme_data = rng.choice(list(self.FALLBACK_THEMES.values()))
                final_lyrics = self.FALLBACK_TEMPLATES["Standard"].format(
                    theme_line_1=theme_data["lines"][0],
                    theme_line_2=theme_data["lines"][1],
                    power_phrase=theme_data["phrase"]
                )

        elif vocal_mode == "All Lyrics":
            # 與 Full Lyrics 相同邏輯，但固定讀取 all.json
            lang_dir_name = self.LANG_DIRS.get(language, "lyrics_wildcards_en")
            wildcards_dir = os.path.join(self.BASE_DIR, lang_dir_name)
            json_file_path = os.path.join(wildcards_dir, "all.json")

            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    wildcards_data = json.load(f)

                structure = rng.choice(wildcards_data.get("structures", ["[Verse]\n{verse}\n\n[Chorus]\n{chorus}"]))
                sections = structure.split("\n\n")
                processed_sections = []

                for section in sections:
                    section_pools = {}

                    def replace_tag_block_all(match):
                        tag_name = match.group(1)
                        if tag_name in wildcards_data and isinstance(wildcards_data[tag_name], list) and wildcards_data[tag_name]:
                            if tag_name not in section_pools:
                                pool = list(wildcards_data[tag_name])
                                rng.shuffle(pool)
                                section_pools[tag_name] = pool
                            if not section_pools[tag_name]:
                                pool = list(wildcards_data[tag_name])
                                rng.shuffle(pool)
                                section_pools[tag_name] = pool
                            picked = section_pools[tag_name].pop()
                            if isinstance(picked, list):
                                return str(picked[0]) if picked else ""
                            return str(picked)
                        return match.group(0)

                    processed_section = re.sub(r'\{([^}]+)\}', replace_tag_block_all, section)
                    processed_sections.append(processed_section)

                final_lyrics = "\n\n".join(processed_sections)

            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"[ACE-Step Generator] Warning: 無法讀取 all.json in {lang_dir_name} ({e})。正在使用備用歌詞庫。")
                theme_data = rng.choice(list(self.FALLBACK_THEMES.values()))
                final_lyrics = self.FALLBACK_TEMPLATES["Standard"].format(
                    theme_line_1=theme_data["lines"][0],
                    theme_line_2=theme_data["lines"][1],
                    power_phrase=theme_data["phrase"]
                )

        # 返回參數中增加 language
        return (final_prompt, final_lyrics, bpm, keyscale, language, json_genre_name, selected_mood.split('_')[0])


# 節點註冊
NODE_CLASS_MAPPINGS = {
    "AceStep15PromptGenerator": AceStep15PromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceStep15PromptGenerator": "🎹 ACE-Step 1.5 Auto-Producer (Multi-language)"
}