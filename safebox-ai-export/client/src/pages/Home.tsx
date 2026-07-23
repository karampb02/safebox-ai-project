import { Button } from "@/components/ui/button";
import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Loader2, ShieldCheck, ShieldAlert, Link as LinkIcon, Sparkles } from "lucide-react";

export default function Home() {
  const [url, setUrl] = useState("");
  const checkUrlMutation = trpc.ai.checkUrl.useMutation();

  const handleCheckUrl = () => {
    if (!url) return;
    let formattedUrl = url;
    if (!/^https?:\/\//i.test(formattedUrl)) {
      formattedUrl = "https://" + formattedUrl;
    }
    checkUrlMutation.mutate({ url: formattedUrl });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 relative overflow-hidden">
      {/* Dynamic Background Gradients */}
      <div className="absolute top-0 inset-x-0 h-[500px] pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/20 via-purple-500/5 to-transparent opacity-60"></div>
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[80%] rounded-full bg-indigo-600/20 blur-[120px]"></div>
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[60%] rounded-full bg-fuchsia-600/20 blur-[120px]"></div>
      </div>

      <header className="px-8 py-6 relative z-10 flex justify-between items-center border-b border-white/5 backdrop-blur-md bg-slate-950/50">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            SafeBox <span className="font-medium text-indigo-400">AI</span>
          </h1>
        </div>
      </header>
      
      <main className="flex-1 p-6 flex flex-col items-center justify-center relative z-10">
        <div className="w-full max-w-3xl space-y-10 animate-in fade-in slide-in-from-bottom-8 duration-1000">
          
          <div className="text-center space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium mb-4">
              <Sparkles className="w-4 h-4" /> Powered by Google Gemini 2.5
            </div>
            <h2 className="text-5xl font-extrabold tracking-tight leading-tight">
              Analyze links with <br/>
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-fuchsia-400">
                Superhuman Intelligence
              </span>
            </h2>
            <p className="text-lg text-slate-400 max-w-xl mx-auto leading-relaxed">
              Instantly detect phishing attempts, scams, and malicious domains before you click. Stay one step ahead of cyber threats.
            </p>
          </div>

          {/* Interactive URL Input Area */}
          <div className="p-2 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl shadow-2xl shadow-black/50 transition-all hover:bg-white/[0.07]">
            <div className="flex items-center gap-2">
              <div className="relative flex-1 group">
                <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 h-5 w-5 transition-colors group-focus-within:text-indigo-400" />
                <input
                  type="url"
                  placeholder="Paste a suspicious link here..."
                  className="w-full pl-12 pr-4 py-4 bg-transparent border-none focus:ring-0 outline-none text-lg placeholder:text-slate-500 transition-all"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCheckUrl()}
                />
              </div>
              <Button 
                onClick={handleCheckUrl} 
                disabled={!url || checkUrlMutation.isPending}
                className="py-6 px-8 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/25 border-none transition-all hover:scale-105 active:scale-95 font-semibold text-lg"
              >
                {checkUrlMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  "Scan URL"
                )}
              </Button>
            </div>
          </div>

          {/* Error State */}
          {checkUrlMutation.error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm text-left animate-in fade-in zoom-in-95 backdrop-blur-md flex items-center gap-3">
              <ShieldAlert className="w-5 h-5 shrink-0" />
              {checkUrlMutation.error.message}
            </div>
          )}

          {/* Results Area */}
          {checkUrlMutation.data && (
            <div className={`p-6 md:p-8 rounded-2xl border backdrop-blur-xl shadow-2xl text-left animate-in slide-in-from-bottom-4 fade-in duration-500 ${
              checkUrlMutation.data.isSpam 
                ? "bg-rose-950/30 border-rose-500/30 shadow-rose-900/20" 
                : "bg-emerald-950/30 border-emerald-500/30 shadow-emerald-900/20"
            }`}>
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className={`p-4 rounded-2xl shrink-0 shadow-inner ${
                  checkUrlMutation.data.isSpam 
                    ? "bg-rose-500/20 text-rose-400 border border-rose-500/20" 
                    : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/20"
                }`}>
                  {checkUrlMutation.data.isSpam ? <ShieldAlert className="h-10 w-10" /> : <ShieldCheck className="h-10 w-10" />}
                </div>
                <div className="space-y-3">
                  <h3 className={`text-2xl font-bold tracking-tight ${
                    checkUrlMutation.data.isSpam ? "text-rose-400" : "text-emerald-400"
                  }`}>
                    {checkUrlMutation.data.isSpam ? "High Risk Detected!" : "URL Verified Safe."}
                  </h3>
                  <div className="h-px w-full bg-white/10 my-4"></div>
                  <p className="text-slate-300 text-lg leading-relaxed">
                    {checkUrlMutation.data.reason}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
