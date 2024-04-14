from .app import main

try:
    main()
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"error: {e}")
    exit(1)
