import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Header from '../../components/header/Header';
import Footer from '../../components/footer/Footer';
import acsApi from '../../api/apiService';
import './LandingPage.css';

const LandingPage = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [journals, setJournals] = useState([]);
  const [news, setNews] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  // Featured journal
  const featuredJournal = {
    title: 'International Transactions in Applied Sciences',
    subtitle: 'Featured Journal',
    description: 'The International Transactions in Applied Sciences (ITAS) is an international research journal, which publishes top-level work on applied sciences. The Journal ITAS is a direct successor of the Journal ITMSC with the aim of publishing papers in all areas of the applied science...',
    logo: 'itas',
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch journals
        const journalsData = await acsApi.journals.listJournals();
        setJournals(journalsData.slice(0, 3) || []);

        // Fetch news/announcements from backend
        try {
          const newsResponse = await acsApi.news.list(0, 10);
          const newsData = newsResponse?.data || [];
          
          // Separate news into articles and announcements
          // Articles can be all news, announcements shows recent ones with badges
          setNews(newsData.slice(0, 4));
          
          // Transform news data to announcements format with type badges
          const announcementData = newsData.slice(0, 4).map((item, index) => {
            const typeColors = ['blue', 'green', 'red', 'gray'];
            const types = ['Update', 'News', 'Important', 'Info'];
            return {
              id: item.id,
              title: item.title,
              date: item.added_on || new Date().toISOString().split('T')[0],
              type: types[index % types.length],
              typeColor: typeColors[index % typeColors.length],
              description: item.description,
              journal_name: item.journal_name
            };
          });
          setAnnouncements(announcementData);
        } catch (newsError) {
          console.log('News not available:', newsError);
          // Set mock announcements as fallback
          setAnnouncements([
            {
              id: 1,
              title: 'AACS Journal Rankings Updated',
              date: '2024-02-12',
              type: 'Update',
              typeColor: 'blue',
            },
            {
              id: 2,
              title: 'New Editorial Board Members',
              date: '2024-02-09',
              type: 'Staff',
              typeColor: 'gray',
            },
          ]);
        }

        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`${isDarkMode ? 'dark' : ''} landing-page-wrapper`}>
      <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 transition-colors duration-200 min-h-screen flex flex-col">
        <Header />

        <main className="flex-1">
          {/* Featured Journal Section */}
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-none overflow-hidden border border-slate-100 dark:border-gray-700">
              <div className="grid md:grid-cols-2 gap-8 items-center">
                {/* Content Side */}
                <div className="p-8 lg:p-16">
                  <div className="inline-flex items-center space-x-2 bg-primary/10 text-primary px-3 py-1 rounded-full mb-6">
                    <span className="text-xs font-bold uppercase tracking-wider">Featured Journal</span>
                  </div>
                  <h2 className="text-4xl lg:text-5xl font-display text-slate-900 dark:text-white mb-6 leading-tight">
                    {featuredJournal.title}
                  </h2>
                  <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed text-lg">
                    {featuredJournal.description}
                    <Link to="/journals" className="text-primary font-semibold hover:underline ml-1">
                      Read more
                    </Link>
                  </p>
                  <div className="flex space-x-4">
                    <Link
                      to="/journals"
                      className="bg-primary hover:bg-red-700 text-white px-8 py-3 rounded-xl font-bold transition-all transform hover:scale-105 shadow-lg shadow-primary/20"
                    >
                      View Journal
                    </Link>
                    <Link
                      to="/journals"
                      className="border-2 border-slate-200 dark:border-gray-700 hover:bg-slate-50 dark:hover:bg-gray-700 px-8 py-3 rounded-xl font-bold transition-all"
                    >
                      Editorial Board
                    </Link>
                  </div>
                </div>

                {/* Illustration Side */}
                <div className="bg-slate-50 dark:bg-gray-900 h-full p-12 flex items-center justify-center relative overflow-hidden min-h-96">
                  <div className="relative z-10 scale-125 md:scale-150">
                    <div className="flex items-end">
                      <div className="text-9xl font-black text-slate-800 dark:text-white tracking-tighter relative">
                        it<span className="text-primary">a</span>s
                        <div className="absolute -top-12 left-2 flex space-x-1">
                          <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></div>
                          <div className="w-4 h-4 rounded-full bg-cyan-400/60"></div>
                          <div className="w-6 h-6 rounded-full bg-cyan-400/30"></div>
                        </div>
                      </div>
                    </div>
                    <div className="h-2 w-full bg-slate-800 dark:bg-white mt-2"></div>
                    <div className="h-2 w-2/3 bg-orange-500 mt-1"></div>
                  </div>
                  <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -mr-32 -mt-32"></div>
                  <div className="absolute bottom-0 left-0 w-48 h-48 bg-secondary/5 rounded-full -ml-24 -mb-24"></div>
                </div>
              </div>
            </div>
          </section>

          {/* Explore Our Journals Section */}
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="flex justify-between items-end mb-10">
              <div>
                <h2 className="text-3xl font-display font-bold text-slate-900 dark:text-white">Explore Our Journals</h2>
                <p className="text-slate-500 dark:text-slate-400 mt-2">Specialized publications for advancement in various fields</p>
              </div>
              <Link to="/journals" className="group flex items-center space-x-2 text-primary font-bold hover:text-red-700 transition-colors">
                <span>View All Journals</span>
                <span className="material-icons text-sm group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </Link>
            </div>

            {/* Journal Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {journals.length > 0 ? (
                journals.map((journal) => (
                  <div
                    key={journal.id}
                    className="group bg-white dark:bg-gray-800 p-8 rounded-3xl border border-slate-100 dark:border-gray-700 shadow-lg shadow-slate-200/50 dark:shadow-none transition-all hover:-translate-y-2 hover:shadow-2xl"
                  >
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-6 group-hover:text-primary transition-colors h-14 overflow-hidden">
                      {journal.name || journal.title}
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center text-sm py-2 border-b border-slate-50 dark:border-gray-700">
                        <span className="text-slate-400">Chief Editor</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300">{journal.chiefEditor || 'NA'}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm py-2 border-b border-slate-50 dark:border-gray-700">
                        <span className="text-slate-400">ISSN Online</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300 italic">{journal.issnOnline || 'Still Waiting'}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm py-2">
                        <span className="text-slate-400">ISSN Print</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300">{journal.issnPrint || '-'}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-12">
                  <p className="text-slate-400">Loading journals...</p>
                </div>
              )}
            </div>
          </section>

          {/* Latest Articles and Announcements Section */}
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 mb-20">
            <div className="grid md:grid-cols-2 gap-12">
              {/* Latest Articles */}
              <div className="flex flex-col">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <span className="material-icons text-primary">description</span>
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Latest Articles</h2>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-3xl border border-slate-100 dark:border-gray-700 shadow-xl shadow-slate-200/50 dark:shadow-none p-2">
                  <div className="scroll-container max-h-[400px] overflow-y-auto px-6 py-4">
                    {news.length > 0 ? (
                      news.map((article) => (
                        <div
                          key={article.id}
                          className="group py-5 border-b border-slate-100 dark:border-gray-700 last:border-0 hover:bg-slate-50/50 dark:hover:bg-gray-700/30 px-4 -mx-4 rounded-xl transition-colors cursor-pointer"
                        >
                          <h4 className="font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                            {article.title || article.name}
                          </h4>
                          {article.description && (
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                              {article.description}
                            </p>
                          )}
                          <div className="flex items-center space-x-2 mt-2">
                            <span className="text-xs font-medium text-slate-400">
                              {article.added_on ? new Date(article.added_on).toLocaleDateString() : (article.createdAt ? new Date(article.createdAt).toLocaleDateString() : 'Recent')}
                            </span>
                            {article.journal_name && (
                              <>
                                <span className="w-1 h-1 bg-slate-300 rounded-full"></span>
                                <span className="text-xs text-primary font-bold">{article.journal_name}</span>
                              </>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-slate-400">No articles yet</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Announcements */}
              <div className="flex flex-col">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-secondary/10 rounded-lg">
                    <span className="material-icons text-secondary">campaign</span>
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Announcements</h2>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-3xl border border-slate-100 dark:border-gray-700 shadow-xl shadow-slate-200/50 dark:shadow-none p-2">
                  <div className="scroll-container max-h-[400px] overflow-y-auto px-6 py-4">
                    {announcements.length > 0 ? (
                      announcements.map((announcement) => {
                        const badgeClasses = {
                          blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
                          gray: 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400',
                          red: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
                          green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
                        };

                        return (
                          <div
                            key={announcement.id}
                            className="group py-5 border-b border-slate-100 dark:border-gray-700 last:border-0 hover:bg-slate-50/50 dark:hover:bg-gray-700/30 px-4 -mx-4 rounded-xl transition-colors cursor-pointer"
                          >
                            <div className="flex justify-between items-start">
                              <h4 className="font-bold text-slate-900 dark:text-white group-hover:text-secondary transition-colors flex-1">
                                {announcement.title}
                              </h4>
                              <span
                                className={`${badgeClasses[announcement.typeColor]} text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider whitespace-nowrap ml-2 flex-shrink-0`}
                              >
                                {announcement.type}
                              </span>
                            </div>
                            <span className="text-xs font-medium text-slate-400 mt-2 block">
                              {announcement.date}
                            </span>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-slate-400">No announcements yet</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>

        <Footer />

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleDarkMode}
          className="fixed bottom-8 right-8 bg-white dark:bg-gray-800 border border-slate-200 dark:border-gray-700 w-12 h-12 rounded-full shadow-2xl flex items-center justify-center text-slate-800 dark:text-white hover:scale-110 transition-transform z-[100]"
          aria-label="Toggle dark mode"
        >
          <span className="material-icons">{isDarkMode ? 'light_mode' : 'dark_mode'}</span>
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
