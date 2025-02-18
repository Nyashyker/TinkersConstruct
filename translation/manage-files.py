#!/usr/bin/python
from io import TextIOWrapper
from pathlib import Path
from typing import Generator


def gather(path: Path, *, collect: bool = False) -> Generator[Path, None, None]:
    """Збирає всі файли мови, з якої буде переклад"""
    for dir_file in path.iterdir():
        if dir_file.stem.startswith("."):
            continue

        if collect or dir_file.stem == TRANSLETE_FROM:
            if dir_file.is_file():
                yield dir_file
            elif dir_file.is_dir():
                yield from gather(dir_file, collect=True)

        elif dir_file.is_dir():
            yield from gather(dir_file, collect=False)


def collect_in_one(folder: Path, file: TextIOWrapper) -> None:
    """Зберігає всі зібрані файли в один"""
    for add_file in gather(folder):
        print(add_file)

        print(add_file.as_posix(), file=file)
        print("```", file=file)
        print(add_file.read_text(encoding="UTF-8").strip(), file=file)
        print("```", end="\n\n", file=file)


def spread_all_over(folder: Path, file: TextIOWrapper, language: str) -> None:
    """Розносить збережені виписки назад по файлах"""

    write_mode: bool = False
    save_file: TextIOWrapper | None = None

    for line in file:
        if line == "```\n":
            write_mode = not write_mode

        elif write_mode:
            # save_file has not be None at this point
            save_file.write(line)

        elif line == "\n":
            pass

        else:
            index: int = line.index(TRANSLETE_FROM)

            if line[index - 1] == "/" and line[index + 5] in {"/", "."}:
                name: Path = folder / line.rstrip().replace(TRANSLETE_FROM, language, 1)
            else:
                raise ValueError(f"`{line}` was not expected")

            name.parent.mkdir(parents=True, exist_ok=True)
            if save_file is not None:
                save_file.close()
            save_file = name.open("wt", encoding="UTF-8")


def main(
    language: str,
    collect_or_spread: bool = True,
    *,
    folder: Path = Path(),
    file: Path = Path("translation/all-in-one.txt"),
) -> None:
    if collect_or_spread:
        with file.open("wt", encoding="UTF-8") as save_file:
            collect_in_one(folder, save_file)

    else:
        with file.open("rt", encoding="UTF-8") as load_file:
            spread_all_over(folder, load_file, language)


TRANSLETE_FROM: str = "en_us"

if __name__ == "__main__":
    main("uk_ua", True)
