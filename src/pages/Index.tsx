import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Featured from "@/components/Featured";
import NewReleases from "@/components/NewReleases";
import Promo from "@/components/Promo";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <main className="min-h-screen">
      <Header />
      <Hero />
      <NewReleases />
      <Featured />
      <Promo />
      <Footer />
    </main>
  );
};

export default Index;