import os
import random
import re
import sqlite3
import threading

import requests
from sopel import plugin

URL_REGEX = re.compile(r"https?://\S+")

NO_MARKOV = "Markov chains are not enabled in this channel."

_load_thread = None
_load_lock = threading.Lock()
_db_path = None


def setup(bot):
    global _db_path
    _db_path = os.path.join(bot.settings.homedir, "markov.db")
    conn = sqlite3.connect(_db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS markov (
                channel     TEXT    NOT NULL,
                first_word  TEXT,
                second_word TEXT,
                third_word  TEXT,
                frequency   INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (channel, first_word, second_word, third_word)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@plugin.rule(r".+")
def on_channel_message(bot, trigger):
    if trigger.is_privmsg:
        return

    channel = str(trigger.sender)
    markov_chance = int(bot.db.get_channel_value(channel, "markov-chance") or 0)

    if markov_chance > 0 and random.randint(0, 99) < markov_chance:
        words = trigger.group(0).split()
        random.shuffle(words)
        for word in words:
            out = _generate(channel, [word])
            if out:
                bot.say(out)
                break

    if bot.db.get_channel_value(channel, "markov"):
        _create(bot, channel, trigger.group(0))


@plugin.command("markov")
@plugin.require_chanmsg("This command only works in channels.")
def cmd_markov(bot, trigger):
    channel = str(trigger.sender)
    if not bot.db.get_channel_value(channel, "markov"):
        return bot.reply(NO_MARKOV)

    first_words = trigger.group(2).split() if trigger.group(2) else []
    out = _generate(channel, first_words)
    if out is not None:
        bot.say(out)
    else:
        bot.reply("Failed to generate a Markov chain.")


@plugin.command("markovfor")
def cmd_markovfor(bot, trigger):
    if not trigger.group(2):
        return bot.reply("Usage: !markovfor <#channel> [seed-word]")

    parts = trigger.group(2).split()
    target_name = parts[0]
    first_words = parts[1:]

    if target_name not in bot.channels:
        return bot.reply("Unknown channel.")

    channel = bot.channels[target_name]
    channel_name = str(channel.name)

    if trigger.is_privmsg and trigger.nick not in channel.users:
        return bot.reply(
            "You must be in %s to run this from a private message." % channel_name
        )

    if not bot.db.get_channel_value(channel_name, "markov"):
        return bot.reply(NO_MARKOV)

    out = _generate(channel_name, first_words)
    if out is not None:
        bot.say(out)
    else:
        bot.reply("Failed to generate a Markov chain.")


@plugin.command("markovon")
@plugin.require_chanmsg("This command only works in channels.")
@plugin.require_privilege(plugin.OP, "You must be a channel operator to use this command.")
def cmd_markovon(bot, trigger):
    channel = str(trigger.sender)
    bot.db.set_channel_value(channel, "markov", True)
    bot.reply("Markov chains enabled for %s." % channel)


@plugin.command("markovoff")
@plugin.require_chanmsg("This command only works in channels.")
@plugin.require_privilege(plugin.OP, "You must be a channel operator to use this command.")
def cmd_markovoff(bot, trigger):
    channel = str(trigger.sender)
    bot.db.set_channel_value(channel, "markov", False)
    bot.reply("Markov chains disabled for %s." % channel)


@plugin.command("markovchance")
@plugin.require_chanmsg("This command only works in channels.")
@plugin.require_privilege(plugin.OP, "You must be a channel operator to use this command.")
def cmd_markovchance(bot, trigger):
    value = trigger.group(2)
    if not value:
        current = bot.db.get_channel_value(str(trigger.sender), "markov-chance") or 0
        return bot.reply("Current random trigger chance: %s%%" % current)

    if not value.isdigit() or not 0 <= int(value) <= 100:
        return bot.reply("Usage: !markovchance <0-100>")

    bot.db.set_channel_value(str(trigger.sender), "markov-chance", int(value))
    bot.reply("Markov random trigger chance set to %s%%." % value)


@plugin.command("clearmarkov")
@plugin.require_chanmsg("This command only works in channels.")
@plugin.require_privilege(plugin.OWNER, "You must be the channel owner to use this command.")
def cmd_clearmarkov(bot, trigger):
    channel = str(trigger.sender)

    if channel == "#premium":
        return bot.reply("The Markov chain for this channel cannot be cleared.")

    conn = sqlite3.connect(_db_path)
    try:
        conn.execute(
            "DELETE FROM markov WHERE channel = :channel",
            {"channel": channel},
        )
        conn.commit()
    finally:
        conn.close()

    bot.reply("Cleared the Markov chain for %s." % channel)


@plugin.command("markovlog")
@plugin.require_chanmsg("This command only works in channels.")
@plugin.require_privilege(plugin.OP, "You must be a channel operator to load logs.")
def cmd_markovlog(bot, trigger):
    global _load_thread

    channel = str(trigger.sender)
    if not bot.db.get_channel_value(channel, "markov"):
        return bot.reply(NO_MARKOV)

    url = trigger.group(2)
    if not url:
        return bot.reply("Usage: !markovlog <url>")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        return bot.reply("Failed to fetch log: %s" % exc)

    with _load_lock:
        if _load_thread is not None and _load_thread.is_alive():
            return bot.reply("A log import is already in progress.")
        bot.reply("Importing...")
        _load_thread = threading.Thread(
            target=_load_loop,
            args=(bot, channel, response.text),
            daemon=True,
        )
        _load_thread.start()


def _load_loop(bot, channel, data):
    global _load_thread
    try:
        for line in data.split("\n"):
            line = line.strip()
            if line:
                _create(bot, channel, line)
    finally:
        _load_thread = None


def _create(bot, channel, line):
    if URL_REGEX.search(line):
        return

    words = [w.lower() for w in line.split() if w]
    if len(words) <= 2:
        return

    inserts = [
        (None, None, words[0]),
        (None, words[0], words[1]),
    ]
    for i in range(len(words) - 2):
        inserts.append(tuple(words[i : i + 3]))
    inserts.append((words[-2], words[-1], None))

    conn = sqlite3.connect(_db_path)
    try:
        for first, second, third in inserts:
            conn.execute(
                """
                INSERT OR REPLACE INTO markov
                    (channel, first_word, second_word, third_word, frequency)
                VALUES (
                    :channel, :first, :second, :third,
                    COALESCE((
                        SELECT frequency FROM markov
                         WHERE channel     IS :channel
                           AND first_word  IS :first
                           AND second_word IS :second
                           AND third_word  IS :third
                    ), 0) + 1
                )
                """,
                {"channel": channel, "first": first, "second": second, "third": third},
            )
        conn.commit()
    finally:
        conn.close()


def _choose(pairs):
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights, k=1)[0]


def _generate(channel, first_words):
    first_words = [w.lower() for w in first_words]
    conn = sqlite3.connect(_db_path)
    try:
        if not first_words:
            rows = conn.execute(
                """
                SELECT third_word, frequency FROM markov
                 WHERE channel     = :channel
                   AND first_word  IS NULL
                   AND second_word IS NULL
                   AND third_word  IS NOT NULL
                """,
                {"channel": channel},
            ).fetchall()
            if not rows:
                return None
            first_word = _choose(rows)

            rows = conn.execute(
                """
                SELECT third_word, frequency FROM markov
                 WHERE channel     = :channel
                   AND first_word  IS NULL
                   AND second_word = :second
                   AND third_word  IS NOT NULL
                """,
                {"channel": channel, "second": first_word},
            ).fetchall()
            if not rows:
                return None

            second_word = _choose(rows)
            words = [first_word, second_word]

        elif len(first_words) == 1:
            first_word = first_words[0]
            rows = conn.execute(
                """
                SELECT second_word, third_word, frequency FROM markov
                 WHERE channel     = :channel
                   AND first_word  = :first
                   AND second_word IS NOT NULL
                   AND third_word  IS NOT NULL
                """,
                {"channel": channel, "first": first_word},
            ).fetchall()
            if not rows:
                return None

            second_word, third_word = _choose(
                [((s, t), f) for s, t, f in rows]
            )
            words = [first_word, second_word, third_word]

        else:
            words = list(first_words)

        for _ in range(30):
            rows = conn.execute(
                """
                SELECT third_word, frequency FROM markov
                 WHERE channel     = :channel
                   AND first_word  = :first
                   AND second_word = :second
                """,
                {"channel": channel, "first": words[-2], "second": words[-1]},
            ).fetchall()
            if not rows:
                break

            next_word = _choose(rows)
            if next_word is None:
                break

            words.append(next_word)
    finally:
        conn.close()

    if words == first_words:
        return None

    return " ".join(words)
