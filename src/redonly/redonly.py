import requests
import os
import markdown
import shutil
import logging
from enum import auto
from strenum import StrEnum
from datetime import datetime
from urllib.parse import urlparse, urljoin
from PIL import Image
from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = "9999.9999.9999-githubclone"


def download_image(img_url: str, is_thumbnail: bool, out_folder: str) -> str:
    a = urlparse(img_url)
    img_name = os.path.basename(a.path)
    img_out = os.path.join(out_folder, img_name)
    clean_url = urljoin(img_url, a.path)
    response = requests.get(clean_url)
    with open(img_out, 'wb') as out_file:
        out_file.write(response.content)

    try:
        img = Image.open(img_out)
        q = 50 if is_thumbnail else 90
        if is_thumbnail:
            size = img.size
            factor = min(size)/50
            img = img.resize((int(size[0]/factor) + 1, int(size[1]/factor) + 1), Image.LANCZOS)
        img.save(img_out, optimize=True, quality=q)
        return img_name
    except Exception:
        os.remove(img_out)
        return ""


class Language(StrEnum):
    en = auto()
    fr = auto()


class Style(StrEnum):
    original = auto()


def get_path(f: str, lang: Language) -> str:
    return f"{os.path.dirname(os.path.realpath(__file__))}/data/{lang}/{f}"


class Post:
    def __init__(self, p, lang: Language) -> None:
        self.title = p["title"]
        self.url = p["url"]
        self.author = p["author"]
        self.datetime = p["created"]
        self.domain = p["domain"]
        self.score = p["score"]
        self.thumb_url = p["thumbnail"]
        self.flair = " ".join([x for x in p["link_flair_text"].split(" ") if not x.endswith(":") and not x.startswith(":")]) \
            if p["link_flair_text"] else ""
        self.flair_color = p["link_flair_background_color"] if p["link_flair_background_color"] else "#666"
        self.flair_text_color = p["link_flair_text_color"]
        self.self_post_data = p["selftext"] if p["is_self"] else None
        self.is_image = "post_hint" in p and p["post_hint"] == "image"
        self.lang = lang

    def create_element(self, out_folder: str) -> str:
        element_path = get_path("element.html", self.lang)
        with open(element_path, 'r') as template:
            content = template.read()
            img_name = ""
            if self.thumb_url != "self" and self.thumb_url != "default" and self.thumb_url != "nsfw" and self.thumb_url != "":
                img_name = download_image(self.thumb_url, True, out_folder)
            content = content.replace("$$THUMB_URL$$", img_name)
            content = content.replace("$$TITLE$$", self.title)
            content = content.replace("$$LINK$$", self.url)
            content = content.replace("$$AUTHOR$$", self.author)
            content = content.replace("$$DOMAIN$$", self.domain)
            content = content.replace("$$SCORE$$", f"{self.score}")
            content = content.replace("$$FLAIR$$", self.flair)
            content = content.replace("$$FLAIR_COLOR$$", self.flair_color)
            flair_text_color = "#fff" if self.flair_text_color == "light" else "#333"
            content = content.replace("$$FLAIR_TEXT_COLOR$$", flair_text_color)
            if self.self_post_data is not None:
                self_post_path = get_path("self_post.html", self.lang)
                with open(self_post_path, 'r') as sp:
                    content_sp = sp.read()
                    content_sp = content_sp.replace("$$SELF_POST$$", f"<p>{markdown.markdown(self.self_post_data)}</p>")
                    content = content.replace("$$SELF_POST$$", content_sp)
            elif self.is_image:
                img_name = download_image(self.url, False, out_folder)
                if len(img_name) > 0:
                    self_img_path = get_path("self_image.html", self.lang)
                    with open(self_img_path, 'r') as si:
                        content_si = si.read()
                        content_si = content_si.replace("$$IMG_URL$$", img_name)
                        content = content.replace("$$SELF_POST$$", content_si)
                else:
                    content = content.replace("$$SELF_POST$$", "")
            else:
                content = content.replace("$$SELF_POST$$", "")
            return content


class Subreddit:
    def __init__(self, sub: str, sr_data, lang: Language) -> None:
        self.link_name = sub
        self.description = sr_data["public_description"]
        self.name = sr_data["display_name"]
        self.img = sr_data["community_icon"].split("?")[0]
        self.lang = lang

    def create_element(self, out_folder: str) -> str:
        sub_path = get_path("sub.html", self.lang)
        with open(sub_path, 'r') as template:
            content = template.read()
            img_name = ""
            if self.img != "self" and self.img != "default" and self.img != "nsfw" and self.img != "":
                img_name = download_image(self.img, True, out_folder)
            content = content.replace("$$THUMB_URL$$", img_name)
            content = content.replace("$$TITLE$$", self.name)
            content = content.replace("$$LINK$$", f"{self.link_name}.html")
            content = content.replace("$$DESCRIPTION$$", self.description)
            return content


class RedOnly:
    def __init__(self, out_folder: str, subreddits, lang: Language = Language.en, style: Style = Style.original) -> None:
        self.out_folder = out_folder
        self.subreddits = sorted(subreddits, key=lambda v: v.upper())
        self.lang = lang
        self.style = style

    @staticmethod
    def version() -> str:
        return __version__

    @staticmethod
    def _get_headers() -> dict:
        return {
            "Authorization": None,
            "User-Agent": f"RedOnly/{RedOnly.version()}",
            "Content-type": "application/json",
            "Accept": "application/json",
        }

    def _write_subreddit(self, sub: str) -> bool:
        s = requests.Session()
        refresh_date = f'{datetime.now():%d %B %Y} at {datetime.now():%H:%M}'
        data = s.get(f"https://www.reddit.com/r/{sub}/hot.json", headers=self._get_headers())
        if not data.status_code == 200:
            logging.error(f"Failed to get data ({data.status_code}) for {sub}")
            return False

        j = data.json()
        posts = []
        for p in j["data"]["children"]:
            post = Post(p["data"], self.lang)
            posts.append(post)

        elements = ""
        for p in posts:
            elements += p.create_element(self.out_folder)

        template_path = get_path("template.html", self.lang)
        with open(template_path, 'r') as page:
            content = page.read()
            content = content.replace("$$SUBREDDIT$$", sub)
            content = content.replace("$$ELEMENTS$$", elements)
            content = content.replace("$$LAST_REFRESH_STR$$", refresh_date)
            with open(f"{self.out_folder}/{sub}.html", 'w', encoding='utf-8') as ro_page:
                ro_page.write(content)
        return True

    def _write_index(self) -> bool:
        s = requests.Session()
        subreddits_data = []
        for sub in self.subreddits:
            data = s.get(f"https://www.reddit.com/r/{sub}/about.json", headers=self._get_headers())
            if not data.status_code == 200:
                logging.error(f"Failed to get about data ({data.status_code}) for {sub}")
                return False
            subreddits_data.append(Subreddit(sub, data.json()["data"], self.lang))
        subs = ""
        for sub in subreddits_data:
            subs += sub.create_element(self.out_folder)

        template_path = get_path("template.html", self.lang)
        with open(template_path) as page:
            content = page.read()
            content = content.replace("$$SUBREDDIT$$", "index")
            content = content.replace("$$ELEMENTS$$", subs)
            content = content.replace("$$LAST_REFRESH_STR$$", "now")
            with open(f"{self.out_folder}/index.html", 'w') as ro_page:
                ro_page.write(content)
        return True

    def _set_up_folder(self) -> bool:
        try:
            if os.path.exists(self.out_folder):
                shutil.rmtree(self.out_folder)
        except OSError as e:
            logging.error(f"Failed to clean {self.out_folder}: {e}")
            return False

        try:
            os.makedirs(self.out_folder)
        except OSError as e:
            logging.error(f"Failed to create {self.out_folder}: {e}")
            return False
        return True

    def generate(self) -> bool:
        if not self._set_up_folder():
            return False

        style_path = get_path(f"{self.style}.css", self.lang)
        try:
            shutil.copyfile(style_path, os.path.join(self.out_folder, "style.css"))
        except Exception:
            logging.error(f"Failed to copy style from {style_path}")
            return False

        for sub in self.subreddits:
            logging.info(f"Creating {sub}...")
            if not self._write_subreddit(sub):
                logging.error(f"Failed to write subreddit {sub}")
                return False
        logging.info("Creating index...")
        if not self._write_index():
            logging.error("Failed to write index")
            return False
        logging.info("All done!")
        return True
