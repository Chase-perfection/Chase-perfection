from datetime import datetime, timezone
import re

content = f"Dernière mise à jour : {datetime.now(timezone.utc):%d/%m/%Y %H:%M} UTC"

readme = open("README.md").read()
readme = re.sub(
    r"<!-- START:AUTO -->.*<!-- END:AUTO -->",
    f"<!-- START:AUTO -->\n{content}\n<!-- END:AUTO -->",
    readme,
    flags=re.S,
)
open("README.md", "w").write(readme)
