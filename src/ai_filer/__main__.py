#! /usr/bin/env python3

import sys
import logging as log
from . import main  # Use relative import since we're in the same package

if __name__ == "__main__":
    logger = log.Logger(name="ai_filer")
    try:
        main.main()
    except SystemExit as e:
        logger.exception("Exception:")
        sys.exit(e.code)
    except KeyboardInterrupt:
        raise
    except Exception:  # Catch all other exceptions
        logger.exception("Exception:")

    sys.exit(0)
