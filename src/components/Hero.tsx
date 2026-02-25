import { useScroll, useTransform, motion } from "framer-motion";
import { useRef } from "react";

export default function Hero() {
  const container = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: container,
    offset: ["start start", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], ["0vh", "50vh"]);

  return (
    <div
      ref={container}
      className="relative flex items-center justify-center h-screen overflow-hidden"
    >
      <motion.div
        style={{ y }}
        className="absolute inset-0 w-full h-full"
      >
        <img
          src="/images/mountain-landscape.jpg"
          alt="Mountain landscape"
          className="w-full h-full object-cover"
        />
      </motion.div>

      <div className="relative z-10 text-center text-white px-6">
        <p className="uppercase tracking-widest text-sm mb-4 opacity-70">Всё о кино в одном месте</p>
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6">
          SHELDYXOV
        </h1>
        <p className="text-lg md:text-xl max-w-2xl mx-auto opacity-90">
          Новые фильмы, сериалы и истории актёров — первым узнавай о самом интересном
        </p>
        <button className="mt-8 border border-white text-white px-8 py-3 uppercase tracking-wide text-sm hover:bg-white hover:text-black transition-all duration-300 cursor-pointer">
          Смотреть новинки
        </button>
      </div>
    </div>
  );
}