import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTeams } from '../services/teams';
import { useThreadMessages, useSendMessage } from '../services/threads';
import Select from '../components/common/Select';
import Textarea from '../components/common/Textarea';
import Button from '../components/common/Button';
import Header from '../components/Layout/Header';
import type { ChatMessageRead } from '../types/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

const markdownStyles = "prose prose-sm md:prose-base max-w-none dark:prose-invert prose-p:leading-relaxed prose-p:my-1.5 prose-headings:my-3 prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-h4:text-base prose-ul:my-2 prose-ol:my-2 prose-li:my-1";

export default function Chat() {
  const { threadId } = useParams<{ threadId?: string }>();
  const navigate = useNavigate();
  const { data: teams } = useTeams();
  const { data: existingMessages, isLoading: isLoadingMessages } = useThreadMessages(threadId);
  const sendMessage = useSendMessage();

  const [selectedTeamId, setSelectedTeamId] = useState<number | ''>('');
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessageRead[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatAreaRef = useRef<HTMLDivElement>(null);
  const streamingContentRef = useRef<string>('');


  // Load existing messages when threadId changes, but don't overwrite optimistic updates while streaming
  useEffect(() => {
    // Skip updates if streaming is active to preserve optimistic state
    if (isStreaming) return;

    if (existingMessages) {
      let currentMessages = [...existingMessages];



      setMessages(currentMessages);
      // Clear streaming content when messages are refreshed
      setStreamingContent('');
      streamingContentRef.current = '';
    } else {
      setMessages([]);
    }
  }, [existingMessages, isStreaming]);

  // If threadId exists but no team selected, try to get team from localStorage
  useEffect(() => {
    if (threadId && !selectedTeamId) {
      const savedTeamId = localStorage.getItem(`thread_${threadId}_teamId`);
      if (savedTeamId) {
        setSelectedTeamId(Number(savedTeamId));
      }
    }
  }, [threadId, selectedTeamId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const generateThreadId = (): string => {
    return crypto.randomUUID();
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedTeamId || isStreaming) return;

    const messageText = inputMessage.trim();
    setInputMessage('');

    let currentThreadId = threadId;

    // If no threadId, generate one and update URL
    if (!currentThreadId) {
      currentThreadId = generateThreadId();
      navigate(`/chat/${currentThreadId}`, { replace: true });
    }

    // Save team_id to localStorage for this thread
    localStorage.setItem(`thread_${currentThreadId}_teamId`, String(selectedTeamId));

    // Add user message immediately
    const userMessage: ChatMessageRead = {
      id: crypto.randomUUID(),
      type: 'human',
      content: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Start streaming
    setIsStreaming(true);
    setStreamingContent('');
    streamingContentRef.current = '';


    try {
      await sendMessage.mutateAsync({
        threadId: currentThreadId,
        request: {
          message: messageText,
          team_id: selectedTeamId as number,
        },
        onChunk: (chunk: any) => {
          const eventType = chunk.type;



          // 1. Tool Calls (AI requests execution of a tool)
          // We immediately add this as a message
          if (eventType === 'ai' && chunk.tool_calls && chunk.tool_calls.length > 0) {
            setMessages((prev) => [
              ...prev,
              {
                id: crypto.randomUUID(),
                type: 'ai',
                content: chunk.content || '',
                tool_calls: chunk.tool_calls,
                created_at: new Date().toISOString()
              } as ChatMessageRead
            ]);
            // If there's content mixed with tool calls, we might want to capture it, 
            // but usually content is empty or intro text. 
            // If it's empty, we ensure streamingContent is clear for next text.
            setStreamingContent('');
            streamingContentRef.current = '';
          }

          // 2. Tool Output (Result from the tool)
          // We immediately add this as a message
          else if (eventType === 'tool') {
            setMessages((prev) => [
              ...prev,
              {
                id: chunk.tool_call_id || crypto.randomUUID(),
                type: 'tool',
                content: chunk.content || '',
                name: chunk.name,
                tool_call_id: chunk.tool_call_id,
                created_at: new Date().toISOString()
              } as ChatMessageRead
            ]);
            setStreamingContent('');
            streamingContentRef.current = '';
          }

          // 3. AI Answer (Content streaming)
          else if (eventType === 'ai' && chunk.content) {
            if (typeof chunk.content === 'string') {
              streamingContentRef.current += chunk.content;
              setStreamingContent((prev) => prev + chunk.content);
            }
          }
        },
      });

      // Messages will be refreshed automatically by React Query via invalidateQueries
      // Set isStreaming to false, but keep streamingContent visible until messages refresh
      setIsStreaming(false);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message. Please try again.');
      setIsStreaming(false);
      setStreamingContent('');
      streamingContentRef.current = '';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const canSend = selectedTeamId && inputMessage.trim() && !isStreaming;

  return (
    <div className="flex h-full flex-col">
      <Header title="Chat" subtitle="Chat with your AI teams" />
      <div className="flex flex-1 flex-col overflow-hidden p-6">
        {/* Team Selector */}
        <div className="mb-4">
          <Select
            label="Select Team"
            value={selectedTeamId}
            onChange={(e) => setSelectedTeamId(e.target.value ? Number(e.target.value) : '')}
            options={
              teams?.map((team) => ({
                value: team.id,
                label: team.name,
              })) || []
            }
            placeholder="Choose a team..."
          />
          {threadId && messages.length > 0 && !selectedTeamId && (
            <p className="mt-1 text-sm text-gray-500">
              Select a team to continue the conversation
            </p>
          )}
        </div>

        {/* Chat Area */}
        <div
          ref={chatAreaRef}
          className="flex-1 overflow-y-auto rounded-lg border border-gray-200 bg-white p-4 mb-4"
        >
          {isLoadingMessages ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">Loading messages...</div>
            </div>
          ) : messages.length === 0 && !isStreaming ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500">
                {!selectedTeamId
                  ? 'Select a team and start a conversation'
                  : 'Start a conversation by sending a message'}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'human' ? 'justify-end' : 'justify-start'
                    }`}
                >
                  <div
                    className={`${message.type === 'human' ? 'max-w-[80%]' : 'max-w-[70%]'} rounded-lg px-4 py-2 ${message.type === 'human'
                      ? 'bg-primary-600 text-white'
                      : message.type === 'tool'
                        ? 'bg-amber-50 border border-amber-200 text-gray-800' // Highlighted tool output
                        : message.type === 'ai' && message.tool_calls && message.tool_calls.length > 0
                          ? 'bg-blue-50 border border-blue-200 text-gray-800' // Highlighted tool call
                          : 'bg-gray-100 text-gray-900'
                      }`}
                  >
                    {/* Render Content */}
                    {message.type === 'tool' ? (
                      <div className="text-sm font-mono">
                        <div className="font-bold text-xs text-amber-600 mb-1 flex items-center gap-1">
                          <span>📦</span> Tool Output ({message.name})
                        </div>
                        <div className="whitespace-pre-wrap break-words max-h-60 overflow-y-auto custom-scrollbar">
                          {typeof message.content === 'string' ? message.content : JSON.stringify(message.content, null, 2)}
                        </div>
                      </div>
                    ) : message.type === 'human' ? (
                      <div className="whitespace-pre-wrap break-words text-white">
                        {typeof message.content === 'string' 
                          ? message.content 
                          : Array.isArray(message.content) 
                            ? message.content.map((b: any) => b.type === 'text' ? b.text : '').join('\n') 
                            : JSON.stringify(message.content)}
                      </div>
                    ) : (
                      <div className="w-full break-words">
                        {Array.isArray(message.content) ? (
                          <div className="space-y-3">
                            {message.content.map((block: any, index: number) => {
                              if (block.type === 'text') {
                                const isIntermediate = message.tool_calls && message.tool_calls.length > 0;
                                return isIntermediate ? (
                                  <div key={index} className="whitespace-pre-wrap text-gray-700 text-sm">
                                    {block.text}
                                  </div>
                                ) : (
                                  <div key={index} className={markdownStyles}>
                                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                                      {block.text}
                                    </ReactMarkdown>
                                  </div>
                                );
                              }
                              if (block.type === 'tool_use') {
                                return (
                                  <div key={index} className="text-xs bg-white/80 p-2 rounded border border-blue-100">
                                    <div className="font-semibold text-blue-600 flex items-center gap-1">
                                      <span>🛠️</span> Calling:  <span className="font-bold">{block.name}</span>
                                    </div>
                                    <div className="font-mono text-gray-600 mt-1 whitespace-pre-wrap">
                                      {JSON.stringify(block.input, null, 2)}
                                    </div>
                                  </div>
                                );
                              }
                              return null;
                            })}
                          </div>
                        ) : message.tool_calls && message.tool_calls.length > 0 ? (
                          <div className="whitespace-pre-wrap text-gray-700 text-sm">
                            {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
                          </div>
                        ) : (
                          <div className={markdownStyles}>
                            <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                              {typeof message.content === 'string' ? message.content : ''}
                            </ReactMarkdown>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Render Tool Calls for AI messages (Standard / Legacy) */}
                    {message.type === 'ai' && message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="mt-2 space-y-2">
                        {message.tool_calls.map((toolCall: any) => (
                          <div key={toolCall.id} className="text-xs bg-white/80 p-2 rounded border border-blue-100">
                            <div className="font-semibold text-blue-600 flex items-center gap-1">
                              <span>🛠️</span> Calling: {toolCall.name}
                            </div>
                            <div className="font-mono text-gray-600 mt-1 whitespace-pre-wrap">
                              {JSON.stringify(toolCall.args, null, 2)}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}



                    <div
                      className={`text-xs mt-1 ${message.type === 'human' ? 'text-primary-100' : 'text-gray-500'
                        }`}
                    >
                      {new Date(message.created_at || Date.now()).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}

              {/* Streaming message - show during streaming or until messages are refreshed */}
              {(streamingContent || isStreaming) && (
                <div className="flex justify-start">
                  <div className="max-w-[70%] rounded-lg px-4 py-2 bg-gray-100 text-gray-900">
                    {streamingContent && (
                      <div className={`${markdownStyles} mb-1`}>
                        <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                          {streamingContent}
                        </ReactMarkdown>
                      </div>
                    )}
                    {isStreaming && (
                      <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                        <svg className="animate-spin h-3 w-3 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>Generating...</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="flex gap-2">
          <div className="flex-1">
            <Textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                !selectedTeamId && !threadId
                  ? 'Select a team first...'
                  : 'Type your message... (Press Enter to send, Shift+Enter for new line)'
              }
              rows={3}
              disabled={(!selectedTeamId && !threadId) || isStreaming}
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={handleSendMessage}
              disabled={!canSend}
              className="h-full"
            >
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

