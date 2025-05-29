export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-700 p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white sm:text-6xl">
          Sales Prospect Research Tool
        </h1>
        <p className="mt-6 text-lg leading-8 text-slate-300">
          Automated research powered by Gemini.
        </p>
        {/* Login button/form will go here later */}
      </div>
    </main>
  );
}
