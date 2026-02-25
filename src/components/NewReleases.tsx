import { useEffect, useState } from "react";

const TMDB_TOKEN = import.meta.env.VITE_TMDB_TOKEN as string;
const TMDB_BASE = "https://api.themoviedb.org/3";

interface Movie {
  title: string;
  original_title: string;
  type: "film" | "series" | "cartoon";
  year: string;
  genre: string;
  description: string;
  rating: string;
  poster: string | null;
}

const GENRES_MOVIE: Record<number, string> = {
  28: "Экшн", 12: "Приключения", 16: "Мультфильм", 35: "Комедия",
  80: "Криминал", 99: "Документальный", 18: "Драма", 10751: "Семейный",
  14: "Фэнтези", 36: "История", 27: "Ужасы", 53: "Триллер",
  878: "Фантастика", 10749: "Романтика", 37: "Вестерн",
};

const GENRES_TV: Record<number, string> = {
  10759: "Экшн", 35: "Комедия", 80: "Криминал", 99: "Документальный",
  18: "Драма", 10751: "Семейный", 9648: "Детектив", 878: "Фантастика",
  10765: "Фантастика", 10768: "Война",
};

async function tmdbGet(path: string, params: Record<string, string>) {
  const url = new URL(`${TMDB_BASE}${path}`);
  Object.entries({ ...params, language: "ru-RU" }).forEach(([k, v]) =>
    url.searchParams.set(k, v)
  );
  const res = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${TMDB_TOKEN}`,
      Accept: "application/json",
    },
  });
  return res.json();
}

async function fetchReleases(): Promise<Movie[]> {
  const today = new Date().toISOString().slice(0, 10);
  const dateFrom = `${new Date().getFullYear()}-01-01`;

  const [filmsData, cartoonsData, seriesData] = await Promise.all([
    tmdbGet("/discover/movie", {
      sort_by: "popularity.desc",
      "primary_release_date.gte": dateFrom,
      "primary_release_date.lte": today,
      without_genres: "16",
      page: "1",
    }),
    tmdbGet("/discover/movie", {
      sort_by: "popularity.desc",
      "primary_release_date.gte": dateFrom,
      "primary_release_date.lte": today,
      with_genres: "16",
      page: "1",
    }),
    tmdbGet("/discover/tv", {
      sort_by: "popularity.desc",
      "first_air_date.gte": dateFrom,
      "first_air_date.lte": today,
      page: "1",
    }),
  ]);

  type TmdbItem = { title?: string; name?: string; original_title?: string; original_name?: string; release_date?: string; first_air_date?: string; genre_ids?: number[]; overview?: string; vote_average?: number; poster_path?: string; };

  const mapMovie = (m: TmdbItem, type: "film" | "cartoon"): Movie => ({
    title: m.title || m.name || "",
    original_title: m.original_title || m.original_name || "",
    type,
    year: (m.release_date || "").slice(0, 4),
    genre: GENRES_MOVIE[m.genre_ids?.[0] ?? 0] || "Кино",
    description: m.overview || "Описание отсутствует.",
    rating: m.vote_average ? `${m.vote_average.toFixed(1)}/10` : "нет оценки",
    poster: m.poster_path ? `https://image.tmdb.org/t/p/w500${m.poster_path}` : null,
  });

  const mapSeries = (s: TmdbItem): Movie => ({
    title: s.name || "",
    original_title: s.original_name || "",
    type: "series",
    year: (s.first_air_date || "").slice(0, 4),
    genre: GENRES_TV[s.genre_ids?.[0] ?? 0] || "Сериал",
    description: s.overview || "Описание отсутствует.",
    rating: s.vote_average ? `${s.vote_average.toFixed(1)}/10` : "нет оценки",
    poster: s.poster_path ? `https://image.tmdb.org/t/p/w500${s.poster_path}` : null,
  });

  const films = (filmsData.results as TmdbItem[] || []).slice(0, 3).map((m) => mapMovie(m, "film"));
  const cartoons = (cartoonsData.results as TmdbItem[] || []).slice(0, 3).map((m) => mapMovie(m, "cartoon"));
  const series = (seriesData.results as TmdbItem[] || []).slice(0, 3).map(mapSeries);

  return [...films, ...series, ...cartoons];
}

const TYPE_LABEL: Record<string, string> = {
  film: "Фильм",
  series: "Сериал",
  cartoon: "Мультфильм",
};

export default function NewReleases() {
  const [items, setItems] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchReleases()
      .then(setItems)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="bg-neutral-950 py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <p className="uppercase text-xs tracking-widest text-neutral-500 mb-3">
          Новинки {new Date().getFullYear()}
        </p>
        <h2 className="text-3xl lg:text-5xl font-bold text-white mb-12 tracking-tight">
          Фильмы, сериалы и мультфильмы
        </h2>

        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} className="bg-neutral-800 animate-pulse rounded-none h-80" />
            ))}
          </div>
        )}

        {error && (
          <p className="text-neutral-400 text-center py-12">
            Не удалось загрузить новинки. Проверьте TMDB токен.
          </p>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item, i) => (
              <div key={i} className="group relative bg-neutral-900 overflow-hidden cursor-pointer">
                <div className="relative h-72 overflow-hidden">
                  {item.poster ? (
                    <img
                      src={item.poster}
                      alt={item.title}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  ) : (
                    <div className="w-full h-full bg-neutral-800 flex items-center justify-center">
                      <span className="text-neutral-600 text-sm uppercase tracking-wide">Нет постера</span>
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-neutral-900 via-transparent to-transparent" />
                  <span className="absolute top-3 left-3 bg-white text-black text-xs uppercase tracking-wide px-2 py-1 font-medium">
                    {TYPE_LABEL[item.type]}
                  </span>
                  <span className="absolute top-3 right-3 bg-black/70 text-white text-xs px-2 py-1">
                    ★ {item.rating}
                  </span>
                </div>
                <div className="p-4">
                  <p className="text-neutral-500 text-xs uppercase tracking-wide mb-1">
                    {item.genre} · {item.year}
                  </p>
                  <h3 className="text-white font-semibold text-lg leading-tight mb-1 line-clamp-1">
                    {item.title}
                  </h3>
                  <p className="text-neutral-400 text-xs mb-2 italic">{item.original_title}</p>
                  <p className="text-neutral-400 text-sm leading-relaxed line-clamp-3">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}