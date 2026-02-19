class BoltTensionerLibrary:
    data = {
        "M30": {
            "diameter": 30,
            "H1": 220.6,
            "h3_min": 60,
            "h3_max": 78.5,
            "dt_min": 750,
            "H9": 25,
            "C1": 85.5,
            "C2": 34,
            "le_min": 40,
            "t": 65
        },
        "M36": {
            "diameter": 36,
            "H1": 247.5,
            "h3_min": 72,
            "h3_max": 92,
            "dt_min": 1000,
            "H9": 33.5,
            "C1": 90.5,
            "C2": 40.5,
            "le_min": 45,
            "t": 77
        },
        "M42": {
            "diameter": 42,
            "H1": 273.8,
            "h3_min": 84,
            "h3_max": 105,
            "dt_min": 1250,
            "H9": 43.5,
            "C1": 98.5,
            "C2": 47.5,
            "le_min": 51.5,
            "t": 87
        },
        "M48": {
            "diameter": 48,
            "H1": 289.9,
            "h3_min": 94,
            "h3_max": 117,
            "dt_min": 1500,
            "H9": 48.5,
            "C1": 105,
            "C2": 53.5,
            "le_min": 58.5,
            "t": 100
        },
        "M56": {
            "diameter": 56,
            "H1": 410.2,
            "h3_min": 111,
            "h3_max": 134,
            "dt_min": 1750,
            "H9": 64,
            "C1": 111,
            "C2": 58.5,
            "le_min": 65.5,
            "t": 113
        },
        "M64": {
            "diameter": 64,
            "H1": 429.8,
            "h3_min": 125,
            "h3_max": 151,
            "dt_min": 2000,
            "H9": 61,
            "C1": 118,
            "C2": 65.5,
            "le_min": 71,
            "t": 123
        },
        "M72": {
            "diameter": 72,
            "H1": 472.2,
            "h3_min": 140,
            "h3_max": 168,
            "dt_min": 2500,
            "H9": 85.5,
            "C1": 127,
            "C2": 73,
            "le_min": 76.1,
            "t": 137
        },
        "M80": {
            "diameter": 80,
            "H1": 494.8,
            "h3_min": 155,
            "h3_max": 170,
            "dt_min": 3000,
            "H9": 87.5,
            "C1": 132,
            "C2": 86.5,
            "le_min": 91,
            "t": 152
        },

        "M90": {
            "diameter": 90,
            "H1": 523.1,
            "h3_min": 173.75,
            "h3_max": 172.5,
            "dt_min": 3625,
            "H9": 90,
            "C1": 138.25,
            "C2": 103.375,
            "le_min": 110.,
            "t": 170.75
        },
        "M100": {
            "diameter": 100,
            "H1": 551.3,
            "h3_min": 192.5,
            "h3_max": 175,
            "dt_min": 4250,
            "H9": 92.5,
            "C1": 144.5,
            "C2": 120.25,
            "le_min": 129.,
            "t": 189.5
        }

    }

    @classmethod
    def create(cls, key: str):
        """Factory method: return the dict for one bolt size."""
        return cls.data.get(key)


if __name__ == "__main__":
    bolt_tensioner = BoltTensionerLibrary.create("M72")

    a=1
