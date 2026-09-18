import json
import os
import random
import re


class AnyType(str):
    def __new__(cls, value=""):
        return super().__new__(cls, value)

    def __call__(self, __value: object) -> bool:
        return False


class AceStep15PromptGenerator:
    """
    ACE-Step v1.5 natural-language prompt generator with safe wildcard loading,
    shared lyric-generation logic, and validation safeguards.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LANG_DIRS = {
        "en": "lyrics_wildcards_en",
        "zh": "lyrics_wildcards_zh",
        "jp": "lyrics_wildcards_jp",
    }

    GENRE_DATA = {
        "Pop_流行": {
            "bpm": (90, 128),
            "instruments": [
                "shiny synthesizers",
                "a catchy bass groove",
                "crisp electronic beats",
                "acoustic guitar strums",
                "lush vocal harmonies",
                "a bright piano melody",
            ],
            "vibes": ["polished and commercial", "modern and sleek", "sunny and catchy"],
            "dynamics": [
                "flows smoothly with a strong hook",
                "builds to an emotional chorus",
                "keeps a steady danceable groove",
            ],
        },
        "Rock_搖滾樂": {
            "bpm": (110, 150),
            "instruments": [
                "distorted electric guitars",
                "punchy live drums",
                "a strong bassline",
                "power chords",
                "crash cymbals",
            ],
            "vibes": ["raw and rebellious", "gritty and authentic", "stadium-filling"],
            "dynamics": [
                "builds dynamically from tension to explosion",
                "maintains a driving, relentless rhythm",
                "features explosive choruses and quick verses",
            ],
        },
        "EDM_電子舞曲": {
            "bpm": (120, 130),
            "instruments": [
                "massive supersaw synths",
                "a four-on-the-floor kick drum",
                "sidechained basslines",
                "bright arpeggios",
                "risers and impacts",
            ],
            "vibes": ["festival-ready and huge", "energetic and euphoric", "pumping and relentless"],
            "dynamics": [
                "builds up tension to a massive drop",
                "drives forward with unstoppable energy",
                "explodes into a wall of synthetic sound",
            ],
        },
        "Lo-Fi_低保真音樂": {
            "bpm": (70, 90),
            "instruments": [
                "dusty vinyl crackles",
                "a slightly detuned electric piano",
                "a sluggish, muffled drum beat",
                "warm upright bass",
                "subtle nature soundscapes",
            ],
            "vibes": ["nostalgic and cozy", "relaxed and study-focused", "warm and analog"],
            "dynamics": [
                "loops gracefully without ever peaking",
                "creates a comforting background texture",
                "drifts lazily through jazzy chords",
            ],
        },
        "Ambient_氛圍音樂": {
            "bpm": (40, 70),
            "instruments": [
                "swirling granular pads",
                "deep drone textures",
                "ethereal reverb sweeps",
                "minimalist synth bells",
            ],
            "vibes": ["spacious and meditative", "formless and atmospheric", "ethereal and tranquil"],
            "dynamics": [
                "drifts slowly without a clear melody",
                "evolves through subtle timbral shifts",
                "creates a vast sonic landscape",
            ],
        },
        "Drum_Bass_鼓打貝斯": {
            "bpm": (170, 178),
            "instruments": [
                "fast, complex breakbeats",
                "a roaring Reese bass",
                "atmospheric pads",
                "pitch-shifted vocal samples",
                "rapid-fire percussion",
            ],
            "vibes": ["fast-paced and kinetic", "liquid and smooth", "heavy and aggressive"],
            "dynamics": [
                "rushes forward with breakneck speed",
                "drops into a chaotic bass assault",
                "balances serene atmospheres with frantic drums",
            ],
        },
        "Jazz_爵士樂": {
            "bpm": (80, 120),
            "instruments": [
                "a breathy tenor saxophone",
                "a walking upright bass",
                "brushed snare drums",
                "improvisational grand piano",
                "a clean hollow-body guitar",
            ],
            "vibes": ["sophisticated and smooth", "smoky and late-night", "swinging and lively"],
            "dynamics": [
                "ebbs and flows with conversational solos",
                "swings effortlessly with the rhythm section",
                "breathes naturally through dynamic interplay",
            ],
        },
        "Cinematic_電影配樂": {
            "bpm": (60, 100),
            "instruments": [
                "sweeping string sections",
                "booming orchestral percussion",
                "a lonely solo piano",
                "deep brass swells",
                "a subtle choir",
            ],
            "vibes": ["epic and larger-than-life", "intimate and breathtaking", "vast and atmospheric"],
            "dynamics": [
                "slowly swells into a grand crescendo",
                "ebbs and flows like a tide",
                "creates a building sense of awe",
            ],
        },
        "Cinematic_Orchestral_管弦樂電影配樂": {
            "bpm": (70, 140),
            "instruments": [
                "soaring violins",
                "powerful brass sections",
                "thunderous cinematic percussion",
                "tremolo strings",
                "staccato cellos",
            ],
            "vibes": ["epic and grand", "heroic", "intense and dramatic"],
            "dynamics": [
                "builds into a massive orchestral swell",
                "features dramatic pauses and explosive crescendos",
                "commands attention with majestic scale",
            ],
        },
        "Metal_金屬樂": {
            "bpm": (140, 200),
            "instruments": [
                "down-tuned, heavily distorted guitars",
                "rapid double-kick drums",
                "a clanking bass guitar",
                "aggressive blast beats",
                "screaming pitch harmonics",
            ],
            "vibes": ["brutal and aggressive", "dark and intense", "heavy and unforgiving"],
            "dynamics": [
                "crushes with a wall of heavy distortion",
                "switches from blistering speed to a heavy breakdown",
                "pummels the listener with unrelenting force",
            ],
        },
        "J-Pop_日式流行": {
            "bpm": (110, 145),
            "instruments": [
                "bright digital synthesizers",
                "a driving electric bass",
                "crisp electronic drum patterns",
                "an acoustic piano",
                "layered pop vocals",
            ],
            "vibes": ["upbeat and modern", "melodic and energetic", "radio-friendly and sleek"],
            "dynamics": [
                "opens with a catchy synth riff",
                "builds into an anthem-like chorus",
                "features a dynamic breakdown before the final hook",
            ],
        },
    }

    MOOD_DATA = {
        "Happy_快樂": {
            "scale": "Major",
            "adjs": ["uplifting", "joyful", "bright", "positive", "feel-good", "cheerful"],
            "balances": ["joy and sunshine", "energy and smiles", "positivity and light"],
        },
        "Sad_悲傷": {
            "scale": "Minor",
            "adjs": ["melancholic", "heartbreaking", "sorrowful", "tear-jerking", "emotional"],
            "balances": ["sorrow and reflection", "pain and beauty", "loss and longing"],
        },
        "Energetic_活力": {
            "scale": "Major",
            "adjs": ["powerful", "high-energy", "driving", "adrenaline-fueled", "intense"],
            "balances": ["aggression and excitement", "power and rhythm", "motion and force"],
        },
        "Relaxed_放鬆": {
            "scale": "Major",
            "adjs": ["soothing", "laid-back", "chill", "calm", "mellow"],
            "balances": ["calm and warmth", "peace and tranquility", "ease and comfort"],
        },
        "Dark_黑暗": {
            "scale": "Minor",
            "adjs": ["ominous", "scary", "mysterious", "shadowy", "creepy"],
            "balances": ["tension and fear", "mystery and gloom", "suspense and dread"],
        },
        "Romantic_浪漫": {
            "scale": "Minor",
            "adjs": ["intimate", "passionate", "sentimental", "tender", "warm"],
            "balances": ["love and desire", "sweetness and longing", "affection and warmth"],
        },
        "Epic_史詩": {
            "scale": "Minor",
            "adjs": ["grand", "heroic", "legendary", "vast", "triumphant"],
            "balances": ["glory and scale", "power and majesty", "myth and might"],
        },
        "Dreamy_夢幻": {
            "scale": "Major",
            "adjs": ["surreal", "soft", "floating", "ethereal", "hypnotic"],
            "balances": ["fantasy and reality", "clouds and stardust", "sleep and imagination"],
        },
    }

    ROOT_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    FALLBACK_THEMES = {
        "Love": {"lines": ["Looking into your eyes", "Heart beating fast tonight"], "phrase": "Love is all we need"},
        "City": {"lines": ["Neon lights flickering by", "Concrete jungle beneath the sky"], "phrase": "City never sleeps"},
        "Space": {"lines": ["Stars drifting past the glass", "Universe moving way too fast"], "phrase": "Gravity lets go"},
    }

    FALLBACK_TEMPLATES = {
        "Standard": (
            "[Intro]\n(Instrumental)\n\n"
            "[Verse 1]\n{theme_line_1}\n{theme_line_2}\n"
            "Waiting for the moment to arise\n\n"
            "[Chorus]\n{power_phrase}!\nLet the rhythm take control\n\n"
            "[Outro]\nFading out..."
        )
    }

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
        ),
    }

    VOCAL_TIMBRE_MAP = {
        "Female (Clear/Pop)": "featuring clear and bright female vocals",
        "Female (Husky/Soulful)": "featuring soulful, husky female vocals",
        "Female (Ethereal)": "featuring ethereal and breathy female vocals",
        "Male (Deep)": "featuring deep, resonant male vocals",
        "Male (High/Tenor)": "featuring soaring, high-pitched male vocals",
        "Male (Rough/Rock)": "featuring rough, gritty male vocals",
        "Choir": "featuring a powerful background choir",
        "Duet (Male & Female)": "featuring a male and female vocal duet",
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "genre": (["Random"] + list(cls.GENRE_DATA.keys()), {"default": "Random"}),
                "mood": (["Random"] + list(cls.MOOD_DATA.keys()), {"default": "Random"}),
                "vocal_mode": (["Random", "Full Lyrics", "All Lyrics", "Instrumental", "Choir/Humming"], {"default": "Full Lyrics"}),
                "language": (["Random", "en", "zh", "jp"], {"default": "en", "tooltip": "Choose lyric language; Random selects one at random."}),
                "prompt_style": (["Random", "Standard_標準", "Structured_結構化", "Groove_節奏律動", "Cinematic_電影敘事", "Vintage_復古類比"], {"default": "Random"}),
                "vocal_timbre": (["Random", "None"] + list(cls.VOCAL_TIMBRE_MAP.keys()), {"default": "Random", "tooltip": "Specify vocal timbre"}),
            },
            "optional": {
                "extra_prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "Extra prompt text"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", AnyType("*"), AnyType("*"), "STRING", "STRING")
    RETURN_NAMES = ("prompt", "lyrics", "bpm", "keyscale", "language", "genre", "mood")
    FUNCTION = "generate_ace_params"
    CATEGORY = "AI Music/ACE-Step"

    @staticmethod
    def _genre_json_name(genre_name):
        name = str(genre_name or "").strip()
        if not name:
            return "generic"
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^A-Za-z0-9_-]", "", name)
        name = name.strip("_").strip("-")
        return name.lower() or "generic"

    @staticmethod
    def _safe_candidate_names(name):
        value = str(name or "").strip()
        if not value:
            return []
        normalized = re.sub(r"\s+", "_", value)
        normalized = re.sub(r"[^A-Za-z0-9_-]", "", normalized)
        normalized = normalized.strip("_").strip("-")
        names = []
        for candidate in [normalized, normalized.lower(), normalized.replace("_", "-"), normalized.lower().replace("_", "-")]:
            if candidate and candidate not in names:
                names.append(candidate)
        return names

    @staticmethod
    def _ensure_instruments(genre_info):
        base = list(genre_info.get("instruments") or ["synthesizer", "bass", "drums"])
        if len(base) >= 3:
            return base
        while len(base) < 3:
            base.append(base[-1] if base else "synthesizer")
        return base

    @staticmethod
    def _fallback_lyrics(rng):
        theme_data = rng.choice(list(AceStep15PromptGenerator.FALLBACK_THEMES.values()))
        return AceStep15PromptGenerator.FALLBACK_TEMPLATES["Standard"].format(
            theme_line_1=theme_data["lines"][0],
            theme_line_2=theme_data["lines"][1],
            power_phrase=theme_data["phrase"],
        )

    def _build_lyrics_from_json(self, json_path, wildcards_data, rng):
        if not isinstance(wildcards_data, dict):
            return self._fallback_lyrics(rng)

        structure = rng.choice(wildcards_data.get("structures", ["[Verse]\n{verse}\n\n[Chorus]\n{chorus}"]))
        sections = structure.split("\n\n")
        processed_sections = []

        for section in sections:
            section_pools = {}

            def replace_tag_block(match):
                tag_name = match.group(1)
                values = wildcards_data.get(tag_name)
                if not isinstance(values, list) or not values:
                    return match.group(0)

                if tag_name not in section_pools:
                    pool = list(values)
                    rng.shuffle(pool)
                    section_pools[tag_name] = pool

                if not section_pools[tag_name]:
                    pool = list(values)
                    rng.shuffle(pool)
                    section_pools[tag_name] = pool

                picked = section_pools[tag_name].pop()
                if isinstance(picked, list) and picked:
                    return str(picked[0])
                return str(picked)

            processed_sections.append(re.sub(r"\{([^}]+)\}", replace_tag_block, section))

        return "\n\n".join(processed_sections)

    def _resolve_wildcard_path(self, language, vocal_mode, selected_genre):
        lang_dir_name = self.LANG_DIRS.get(language, "lyrics_wildcards_en")
        candidate_dirs = [
            os.path.join(self.BASE_DIR, lang_dir_name),
            os.path.join(self.BASE_DIR, "lyrics_wildcards"),
            self.BASE_DIR,
        ]

        if vocal_mode == "Full Lyrics":
            genre_names = self._safe_candidate_names(selected_genre)
            file_names = []
            for name in genre_names:
                file_names.extend([f"{name}.json", f"{name.lower()}.json", f"{name}.JSON", f"{name.lower()}.JSON"])
            file_names.extend(["all.json", "all.JSON", "lyrics.json", "lyrics.JSON"])
        else:
            file_names = ["all.json", "all.JSON", "lyrics.json", "lyrics.JSON"]

        seen = set()
        for directory in candidate_dirs:
            if not os.path.isdir(directory):
                continue
            for file_name in file_names:
                file_path = os.path.join(directory, file_name)
                if file_path in seen:
                    continue
                seen.add(file_path)
                if os.path.isfile(file_path):
                    return file_path
        return None

    def _load_lyrics_from_mode(self, language, vocal_mode, rng, selected_genre):
        json_path = self._resolve_wildcard_path(language, vocal_mode, selected_genre)
        if json_path is None:
            print(f"[ACE-Step Generator] Warning: No wildcard JSON found for language={language}, mode={vocal_mode}. Falling back to default lyrics.")
            return self._fallback_lyrics(rng)

        try:
            with open(json_path, "r", encoding="utf-8") as handle:
                wildcards_data = json.load(handle)
            return self._build_lyrics_from_json(json_path, wildcards_data, rng)
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            print(f"[ACE-Step Generator] Warning: Unable to read wildcard JSON {json_path} ({exc}). Falling back to default lyrics.")
            return self._fallback_lyrics(rng)

    def generate_ace_params(self, seed, genre, mood, vocal_mode, language, prompt_style, vocal_timbre, extra_prompt=""):
        rng = random.Random(seed) if seed > 0 else random.Random()

        selected_genre = genre if genre != "Random" else rng.choice(list(self.GENRE_DATA.keys()))
        genre_info = self.GENRE_DATA[selected_genre]
        bpm = rng.randint(genre_info["bpm"][0], genre_info["bpm"][1])

        selected_mood = mood if mood != "Random" else rng.choice(list(self.MOOD_DATA.keys()))
        mood_info = self.MOOD_DATA[selected_mood]
        root = rng.choice(self.ROOT_NOTES)
        keyscale = f"{root} {mood_info['scale']}"

        language = language if language != "Random" else rng.choice(["en", "zh", "jp"])
        if vocal_mode == "Random":
            vocal_mode = rng.choice(["Full Lyrics", "All Lyrics", "Instrumental", "Choir/Humming"])

        actual_vocal_string = ""
        if vocal_mode == "Instrumental":
            actual_vocal_string = "pure instrumental, no vocals"
        else:
            chosen_timbre = vocal_timbre
            if chosen_timbre == "Random":
                chosen_timbre = rng.choice(list(self.VOCAL_TIMBRE_MAP.keys()))
            if chosen_timbre not in (None, "None") and chosen_timbre in self.VOCAL_TIMBRE_MAP:
                actual_vocal_string = self.VOCAL_TIMBRE_MAP[chosen_timbre]

        adjs = rng.sample(mood_info["adjs"], min(2, len(mood_info["adjs"])))
        while len(adjs) < 2:
            adjs.append(mood_info["adjs"][0])

        instruments = self._ensure_instruments(genre_info)
        insts = rng.sample(instruments, min(3, len(instruments)))
        while len(insts) < 3:
            insts.append(instruments[len(insts) % len(instruments)])

        vibe = rng.choice(genre_info.get("vibes", ["modern and expressive"]))
        dynamic = rng.choice(genre_info.get("dynamics", ["moves with confident momentum"]))
        balance = rng.choice(mood_info.get("balances", ["energy and emotion"]))

        selected_style_key = prompt_style if prompt_style != "Random" else rng.choice(list(self.PROMPT_TEMPLATES.keys()))
        selected_template = self.PROMPT_TEMPLATES[selected_style_key]

        final_prompt = selected_template.format(
            adj_1=adjs[0],
            adj_2=adjs[1],
            genre=selected_genre.split("_")[0].lower(),
            vibe=vibe,
            bpm=bpm,
            mood=selected_mood.split("_")[0].lower(),
            inst_1=insts[0],
            inst_2=insts[1],
            inst_3=insts[2],
            dynamic=dynamic,
            balance=balance,
        )

        if actual_vocal_string:
            final_prompt = f"{final_prompt}, {actual_vocal_string}"
        if extra_prompt and extra_prompt.strip():
            final_prompt = f"{final_prompt}, {extra_prompt.strip()}"

        final_lyrics = ""
        json_genre_name = self._genre_json_name(selected_genre)

        if vocal_mode == "Instrumental":
            main_inst = insts[0].split()[-1].capitalize() if insts else "Instrument"
            second_inst = insts[1].split()[-1].capitalize() if len(insts) > 1 else "Rhythm section"
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

        elif vocal_mode in ("Full Lyrics", "All Lyrics"):
            final_lyrics = self._load_lyrics_from_mode(language, vocal_mode, rng, selected_genre)

        return (final_prompt, final_lyrics, bpm, keyscale, language, json_genre_name, selected_mood.split("_")[0])


NODE_CLASS_MAPPINGS = {
    "AceStep15PromptGenerator": AceStep15PromptGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceStep15PromptGenerator": "🎹 ACE-Step 1.5 Auto-Producer (Multi-language)",
}
