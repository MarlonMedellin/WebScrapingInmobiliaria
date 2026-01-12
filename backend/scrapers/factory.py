from sqlalchemy.orm import Session
from .fincaraiz import FincaRaizScraper
from .elcastillo import ElCastilloScraper
from .santafe import SantaFeScraper
from .panda import PandaScraper
from .integridad import IntegridadScraper
from .protebienes import ProtebienesScraper
from .lacastellana import CastellanaScraper
from .monserrate import MonserrateScraper
from .aportal import AportalScraper
from .escalainmobiliaria import EscalaInmobiliariaScraper
from .suvivienda import SuViviendaScraper
from .portofino import PortofinoScraper
from .nutibara import NutibaraScraper
from .laaldea import LaAldeaScraper

class ScraperFactory:
    @staticmethod
    def get_scraper(portal_name: str, db: Session):
        if portal_name == "fincaraiz":
            return FincaRaizScraper(db)
        elif portal_name == "elcastillo":
            return ElCastilloScraper(db)
        elif portal_name == "santafe":
            return SantaFeScraper(db)
        elif portal_name == "panda":
            return PandaScraper(db)
        elif portal_name == "integridad":
            return IntegridadScraper(db)
        elif portal_name == "protebienes":
            return ProtebienesScraper(db)
        elif portal_name == "lacastellana":
            return CastellanaScraper(db)
        elif portal_name == "monserrate":
            return MonserrateScraper(db)
        elif portal_name == "aportal":
            return AportalScraper(db)
        elif portal_name == "escalainmobiliaria":
            return EscalaInmobiliariaScraper(db)
        elif portal_name == "suvivienda":
            return SuViviendaScraper(db)
        elif portal_name == "portofino":
            return PortofinoScraper(db)
        elif portal_name == "nutibara":
            return NutibaraScraper(db)
        elif portal_name == "laaldea":
            return LaAldeaScraper(db)
        else:
            raise ValueError(f"Unknown scraper: {portal_name}")
            
    @staticmethod
    def get_all_scrapers(db: Session):
        return [
            FincaRaizScraper(db),
            ElCastilloScraper(db),
            SantaFeScraper(db),
            PandaScraper(db),
            IntegridadScraper(db),
            ProtebienesScraper(db),
            CastellanaScraper(db),
            MonserrateScraper(db),
            AportalScraper(db),
            EscalaInmobiliariaScraper(db),
            SuViviendaScraper(db),
            PortofinoScraper(db),
            NutibaraScraper(db),
            LaAldeaScraper(db)
        ]

