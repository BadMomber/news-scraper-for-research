from src.config import load_config


def main():
    config = load_config()
    pairs = config.all_keyword_pairs
    print(f"Loaded {len(pairs)} keyword pairs across {len(config.search_terms)} categories")
    print(f"Target sites: {', '.join(config.target_sites)}")
    print(f"Date range: {config.date_start} – {config.date_end}")


if __name__ == "__main__":
    main()
