from django.core.management.base import BaseCommand

from places.models import Place, PlaceCategory, Region


class Command(BaseCommand):
    help = "Добавляет или обновляет десять опубликованных исторических мест Таджикистана."

    def handle(self, *args, **options):
        category, _ = PlaceCategory.objects.get_or_create(
            code="historical",
            defaults={
                "name_ru": "Историческое", "name_en": "Historical", "name_tg": "Таърихӣ", "position": 1,
            },
        )
        regions = {}
        for code, ru, en, tg, position in [
            ("dushanbe", "Душанбе", "Dushanbe", "Душанбе", 1),
            ("sugd", "Согдийская область", "Sughd Region", "Вилояти Суғд", 2),
            ("khatlon", "Хатлонская область", "Khatlon Region", "Вилояти Хатлон", 3),
            ("gbao", "Горно-Бадахшанская автономная область", "Gorno-Badakhshan", "Вилояти Мухтори Кӯҳистони Бадахшон", 4),
            ("rrp", "Районы республиканского подчинения", "Districts of Republican Subordination", "Ноҳияҳои тобеи ҷумҳурӣ", 5),
        ]:
            regions[code], _ = Region.objects.get_or_create(
                code=code,
                defaults={"name_ru": ru, "name_en": en, "name_tg": tg, "position": position},
            )

        places = [
            ("Крепость Гиссар", "Hisor Fortress", "Қалъаи Ҳисор", "Историческая крепость и музейный комплекс к западу от Душанбе.", "Historic fortress and museum complex west of Dushanbe.", "Қалъаи таърихӣ ва маҷмааи осорхонаӣ дар ғарби Душанбе.", "rrp", 38.483728, 68.593611, "09:00–18:00", "20", "easy_walk", ["весна", "осень"]),
            ("Саразм", "Sarazm", "Саразм", "Памятник древнего поселения бронзового века у Пенджикента.", "Bronze Age settlement monument near Panjakent.", "Ёдгории шаҳраки асри биринҷӣ дар назди Панҷакент.", "sugd", 39.508600, 67.454200, "09:00–17:00", "30", "easy_walk", ["весна", "лето", "осень"]),
            ("Древний Пенджикент", "Ancient Panjakent", "Панҷакенти қадим", "Археологический городище согдийского периода с руинами храмов и домов.", "Sogdian archaeological site with ruins of temples and homes.", "Ёдгории бостонии суғдӣ бо харобаҳои маъбадҳо ва хонаҳо.", "sugd", 39.485500, 67.617800, "09:00–18:00", "30", "easy_walk", ["весна", "осень"]),
            ("Худжандская крепость", "Khujand Fortress", "Қалъаи Хуҷанд", "Крепость в историческом центре Худжанда рядом с музеем.", "Fortress in Khujand's historic centre beside the museum.", "Қалъа дар маркази таърихии Хуҷанд дар паҳлуи осорхона.", "sugd", 40.285400, 69.621600, "09:00–17:00", "20", "easy_walk", ["весна", "осень"]),
            ("Крепость Ямчун", "Yamchun Fortress", "Қалъаи Ямчун", "Руины древней крепости над Ваханской долиной.", "Ruins of an ancient fortress above the Wakhan Valley.", "Харобаҳои қалъаи бостонӣ болои водии Вахон.", "gbao", 36.969680, 72.260920, "Круглосуточно", None, "need_offroad", ["лето", "осень"]),
            ("Крепость Каахка", "Kahkaha Fortress", "Қалъаи Қаҳқаҳа", "Памирская крепость у Ишкашима, связанная с легендами о богатыре Сиявуше.", "Pamir fortress near Ishkashim, associated with legends of Siyavush.", "Қалъаи Помир дар назди Ишкошим, вобаста ба ривоятҳои Сиёвуш.", "gbao", 36.732200, 71.609300, "Круглосуточно", None, "need_offroad", ["лето", "осень"]),
            ("Аджина-Теппа", "Ajina-Teppa", "Аҷинатеппа", "Буддийский монастырский комплекс VII–VIII веков в Вахшской долине.", "Seventh- to eighth-century Buddhist monastery complex in the Vakhsh Valley.", "Маҷмааи дайри буддоии асрҳои VII–VIII дар водии Вахш.", "khatlon", 37.864328, 68.941847, "09:00–17:00", "20", "easy_walk", ["весна", "осень"]),
            ("Мавзолей Мир Саида Али Хамадони", "Mausoleum of Mir Sayyid Ali Hamadani", "Мақбараи Мир Саид Алии Ҳамадонӣ", "Мавзолей средневекового поэта и мыслителя в Кулябе.", "Mausoleum of the medieval poet and scholar in Kulob.", "Мақбараи шоир ва донишманди асримиёнагӣ дар Кӯлоб.", "khatlon", 37.914000, 69.784000, "08:00–18:00", None, "easy_walk", ["весна", "осень"]),
            ("Мечеть Ходжа Якуба", "Khoja Yakub Mosque", "Масҷиди Хоҷа Яъқуб", "Историческая мечеть и медресе в старой части Душанбе.", "Historic mosque and madrasa in old Dushanbe.", "Масҷид ва мадрасаи таърихӣ дар қисми кӯҳнаи Душанбе.", "dushanbe", 38.576000, 68.790000, "08:00–18:00", None, "easy_walk", ["весна", "осень"]),
            ("Крепость Хулбук", "Hulbuk Fortress", "Қалъаи Ҳулбук", "Столица средневекового Хутталя и археологический музей-заповедник.", "Medieval capital of Khuttal and an archaeological museum reserve.", "Пойтахти асримиёнагии Хуттал ва осорхона-мамнӯъгоҳи бостоншиносӣ.", "khatlon", 37.647300, 69.963700, "09:00–17:00", "30", "easy_walk", ["весна", "осень"]),
        ]
        for name_ru, name_en, name_tg, desc_ru, desc_en, desc_tg, region, lat, lng, hours, fee, difficulty, seasons in places:
            place, created = Place.objects.update_or_create(
                name_ru=name_ru,
                defaults={
                    "name_en": name_en, "name_tg": name_tg,
                    "description_ru": desc_ru, "description_en": desc_en, "description_tg": desc_tg,
                    "category": category, "region": regions[region], "latitude": lat, "longitude": lng,
                    "opening_hours": hours, "entrance_fee": fee, "access_difficulty": difficulty,
                    "recommended_seasons": seasons, "moderation_status": Place.ModerationStatus.PUBLISHED,
                },
            )
            self.stdout.write(f"{'Создано' if created else 'Обновлено'}: {place.name_ru}")
