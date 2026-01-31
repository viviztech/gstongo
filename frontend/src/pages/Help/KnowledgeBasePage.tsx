/**
 * Knowledge Base / FAQ Page
 */
import React, { useState } from 'react';
import {
    MagnifyingGlassIcon,
    BookOpenIcon,
    QuestionMarkCircleIcon,
    DocumentTextIcon,
    ChevronDownIcon,
    ChevronUpIcon,
    TagIcon,
} from '@heroicons/react/24/outline';

// Mock data
const categories = [
    { id: 'gst', name: 'GST Filing', icon: '📊', count: 15 },
    { id: 'itr', name: 'Income Tax', icon: '📄', count: 12 },
    { id: 'tds', name: 'TDS Returns', icon: '💰', count: 8 },
    { id: 'business', name: 'Business Registration', icon: '🏢', count: 10 },
    { id: 'account', name: 'Account & Billing', icon: '💳', count: 6 },
];

const faqs = [
    {
        id: '1',
        category: 'gst',
        question: 'What is the due date for GSTR-1 filing?',
        answer: 'GSTR-1 is due on the 11th of the month following the tax period for monthly filers, and on the 13th of the month following the quarter for quarterly filers (QRMP scheme).',
        tags: ['gstr-1', 'due-date', 'compliance'],
        views: 1250,
    },
    {
        id: '2',
        category: 'gst',
        question: 'How do I claim Input Tax Credit (ITC)?',
        answer: 'To claim ITC, you must have a valid tax invoice, the goods/services must be received, the supplier must have deposited the tax with the government, and the ITC must be claimed within the time limit. Ensure the invoice is reflected in GSTR-2B.',
        tags: ['itc', 'input-tax-credit', 'claim'],
        views: 980,
    },
    {
        id: '3',
        category: 'itr',
        question: 'Which ITR form should I file?',
        answer: 'ITR-1 (Sahaj) is for salaried individuals with income up to ₹50 lakhs. ITR-2 is for individuals with capital gains. ITR-3 is for business income. ITR-4 (Sugam) is for presumptive income under sections 44AD/44ADA.',
        tags: ['itr-form', 'selection', 'filing'],
        views: 2100,
    },
    {
        id: '4',
        category: 'tds',
        question: 'What are the different TDS return forms?',
        answer: 'Form 24Q is for TDS on salary, Form 26Q for non-salary TDS (other than NRI payments), Form 27Q for TDS on payments to NRIs, and Form 27EQ for Tax Collected at Source (TCS).',
        tags: ['tds-forms', '24q', '26q'],
        views: 650,
    },
    {
        id: '5',
        category: 'business',
        question: 'What documents are required for Private Limited Company registration?',
        answer: 'You need: Identity proof (Aadhaar/Passport) and address proof of directors, PAN of directors, passport-size photographs, proof of registered office address (utility bill + NOC from owner), and Digital Signature Certificate (DSC).',
        tags: ['company-registration', 'documents', 'pvt-ltd'],
        views: 1500,
    },
    {
        id: '6',
        category: 'account',
        question: 'How do I download my invoices?',
        answer: 'Go to the Invoices section in your dashboard. Click on the invoice you want to download, then click the "Download PDF" button. You can also download all invoices as a ZIP file from the Invoices page.',
        tags: ['invoice', 'download', 'billing'],
        views: 420,
    },
];

const articles = [
    {
        id: '1',
        title: 'Complete Guide to GST Filing for Beginners',
        excerpt: 'Learn everything you need to know about GST filing, from registration to return submission.',
        category: 'gst',
        readTime: '10 min',
        views: 3500,
    },
    {
        id: '2',
        title: 'Understanding ITR Forms: Which One Should You Choose?',
        excerpt: 'A comprehensive guide to selecting the right ITR form based on your income sources.',
        category: 'itr',
        readTime: '8 min',
        views: 2800,
    },
    {
        id: '3',
        title: 'TDS Compliance: A Step-by-Step Guide',
        excerpt: 'Everything about TDS deduction, deposit, and return filing for businesses.',
        category: 'tds',
        readTime: '12 min',
        views: 1900,
    },
];

const KnowledgeBasePage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [expandedFaq, setExpandedFaq] = useState<string | null>(null);

    const filteredFaqs = faqs.filter((faq) => {
        const matchesSearch = faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
            faq.answer.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = !selectedCategory || faq.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="text-center py-8 bg-gradient-to-br from-primary-500 to-primary-700 text-white rounded-xl">
                <BookOpenIcon className="w-16 h-16 mx-auto mb-4 opacity-90" />
                <h1 className="text-3xl font-bold mb-2">Knowledge Base</h1>
                <p className="text-primary-100 mb-6">Find answers to your questions</p>

                <div className="max-w-xl mx-auto px-4">
                    <div className="relative">
                        <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
                        <input
                            type="text"
                            placeholder="Search FAQs and articles..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-12 pr-4 py-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-white"
                        />
                    </div>
                </div>
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-3 justify-center">
                <button
                    onClick={() => setSelectedCategory(null)}
                    className={`px-4 py-2 rounded-full transition-colors ${!selectedCategory ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 hover:bg-gray-200'
                        }`}
                >
                    All Topics
                </button>
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setSelectedCategory(cat.id)}
                        className={`px-4 py-2 rounded-full transition-colors flex items-center gap-2 ${selectedCategory === cat.id ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 hover:bg-gray-200'
                            }`}
                    >
                        <span>{cat.icon}</span>
                        <span>{cat.name}</span>
                        <span className="text-xs bg-gray-200 px-2 py-0.5 rounded-full">{cat.count}</span>
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* FAQs */}
                <div className="lg:col-span-2">
                    <div className="card">
                        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <QuestionMarkCircleIcon className="w-6 h-6 text-primary-600" />
                            Frequently Asked Questions
                        </h2>

                        <div className="space-y-3">
                            {filteredFaqs.length > 0 ? (
                                filteredFaqs.map((faq) => (
                                    <div
                                        key={faq.id}
                                        className="border rounded-lg overflow-hidden"
                                    >
                                        <button
                                            onClick={() => setExpandedFaq(expandedFaq === faq.id ? null : faq.id)}
                                            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50"
                                        >
                                            <span className="font-medium text-gray-900">{faq.question}</span>
                                            {expandedFaq === faq.id ? (
                                                <ChevronUpIcon className="w-5 h-5 text-gray-400" />
                                            ) : (
                                                <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                                            )}
                                        </button>
                                        {expandedFaq === faq.id && (
                                            <div className="px-4 pb-4 bg-gray-50">
                                                <p className="text-gray-600 mb-3">{faq.answer}</p>
                                                <div className="flex flex-wrap gap-2">
                                                    {faq.tags.map((tag) => (
                                                        <span
                                                            key={tag}
                                                            className="px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded-full flex items-center gap-1"
                                                        >
                                                            <TagIcon className="w-3 h-3" />
                                                            {tag}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-8">
                                    <QuestionMarkCircleIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                                    <p className="text-gray-500">No FAQs found matching your search</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Popular Articles */}
                <div>
                    <div className="card">
                        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <DocumentTextIcon className="w-6 h-6 text-primary-600" />
                            Popular Articles
                        </h2>

                        <div className="space-y-4">
                            {articles.map((article) => (
                                <div
                                    key={article.id}
                                    className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                                >
                                    <h3 className="font-medium text-gray-900 mb-2">{article.title}</h3>
                                    <p className="text-sm text-gray-500 mb-3">{article.excerpt}</p>
                                    <div className="flex items-center justify-between text-xs text-gray-400">
                                        <span>{article.readTime} read</span>
                                        <span>{article.views.toLocaleString()} views</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Contact Support */}
                    <div className="card mt-6 bg-gradient-to-br from-purple-500 to-indigo-600 text-white">
                        <h3 className="font-bold text-lg mb-2">Need More Help?</h3>
                        <p className="text-purple-100 text-sm mb-4">
                            Can't find what you're looking for? Our support team is here to help.
                        </p>
                        <button className="w-full bg-white text-purple-600 font-medium py-2 rounded-lg hover:bg-purple-50 transition-colors">
                            Contact Support
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default KnowledgeBasePage;
