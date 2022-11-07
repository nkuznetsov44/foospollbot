--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Homebrew)
-- Dumped by pg_dump version 14.5 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: userstate; Type: TYPE; Schema: public; Owner: foospoll
--

CREATE TYPE public.userstate AS ENUM (
    'COLLECTING_FIRST_NAME',
    'COLLECTING_LAST_NAME',
    'COLLECTING_PHONE',
    'COLLECTING_RTSF_URL',
    'COLLECTING_PHOTO',
    'IN_REVIEW',
    'ACCEPTED',
    'REJECTED',
    'VOTING',
    'VOTED'
);


ALTER TYPE public.userstate OWNER TO foospoll;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: evks_players; Type: TABLE; Schema: public; Owner: foospoll
--

CREATE TABLE public.evks_players (
    id integer NOT NULL,
    first_name character varying,
    last_name character varying,
    itsf_first_name character varying,
    itsf_last_name character varying,
    itsf_license integer,
    foreigner boolean,
    last_competition_date date
);


ALTER TABLE public.evks_players OWNER TO foospoll;

--
-- Name: evks_players_id_seq; Type: SEQUENCE; Schema: public; Owner: foospoll
--

CREATE SEQUENCE public.evks_players_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.evks_players_id_seq OWNER TO foospoll;

--
-- Name: evks_players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: foospoll
--

ALTER SEQUENCE public.evks_players_id_seq OWNED BY public.evks_players.id;


--
-- Name: telegram_users; Type: TABLE; Schema: public; Owner: foospoll
--

CREATE TABLE public.telegram_users (
    id integer NOT NULL,
    first_name character varying,
    last_name character varying,
    username character varying
);


ALTER TABLE public.telegram_users OWNER TO foospoll;

--
-- Name: telegram_users_id_seq; Type: SEQUENCE; Schema: public; Owner: foospoll
--

CREATE SEQUENCE public.telegram_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telegram_users_id_seq OWNER TO foospoll;

--
-- Name: telegram_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: foospoll
--

ALTER SEQUENCE public.telegram_users_id_seq OWNED BY public.telegram_users.id;


--
-- Name: user_infos; Type: TABLE; Schema: public; Owner: foospoll
--

CREATE TABLE public.user_infos (
    id integer NOT NULL,
    telegram_user_id integer,
    first_name character varying,
    last_name character varying,
    phone character varying,
    rtsf_url character varying,
    evks_player_id integer,
    photo_id uuid,
    state public.userstate,
    created timestamp without time zone DEFAULT now(),
    updated timestamp without time zone
);


ALTER TABLE public.user_infos OWNER TO foospoll;

--
-- Name: user_infos_id_seq; Type: SEQUENCE; Schema: public; Owner: foospoll
--

CREATE SEQUENCE public.user_infos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_infos_id_seq OWNER TO foospoll;

--
-- Name: user_infos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: foospoll
--

ALTER SEQUENCE public.user_infos_id_seq OWNED BY public.user_infos.id;


--
-- Name: vote_options; Type: TABLE; Schema: public; Owner: foospoll
--

CREATE TABLE public.vote_options (
    id integer NOT NULL,
    text text
);


ALTER TABLE public.vote_options OWNER TO foospoll;

--
-- Name: vote_options_id_seq; Type: SEQUENCE; Schema: public; Owner: foospoll
--

CREATE SEQUENCE public.vote_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vote_options_id_seq OWNER TO foospoll;

--
-- Name: vote_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: foospoll
--

ALTER SEQUENCE public.vote_options_id_seq OWNED BY public.vote_options.id;


--
-- Name: vote_results; Type: TABLE; Schema: public; Owner: foospoll
--

CREATE TABLE public.vote_results (
    id integer NOT NULL,
    telegram_user_id integer,
    selected_option_id integer,
    secret_code character varying,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.vote_results OWNER TO foospoll;

--
-- Name: vote_results_id_seq; Type: SEQUENCE; Schema: public; Owner: foospoll
--

CREATE SEQUENCE public.vote_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vote_results_id_seq OWNER TO foospoll;

--
-- Name: vote_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: foospoll
--

ALTER SEQUENCE public.vote_results_id_seq OWNED BY public.vote_results.id;


--
-- Name: evks_players id; Type: DEFAULT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.evks_players ALTER COLUMN id SET DEFAULT nextval('public.evks_players_id_seq'::regclass);


--
-- Name: telegram_users id; Type: DEFAULT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.telegram_users ALTER COLUMN id SET DEFAULT nextval('public.telegram_users_id_seq'::regclass);


--
-- Name: user_infos id; Type: DEFAULT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.user_infos ALTER COLUMN id SET DEFAULT nextval('public.user_infos_id_seq'::regclass);


--
-- Name: vote_options id; Type: DEFAULT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_options ALTER COLUMN id SET DEFAULT nextval('public.vote_options_id_seq'::regclass);


--
-- Name: vote_results id; Type: DEFAULT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_results ALTER COLUMN id SET DEFAULT nextval('public.vote_results_id_seq'::regclass);


--
-- Name: evks_players evks_players_pkey; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.evks_players
    ADD CONSTRAINT evks_players_pkey PRIMARY KEY (id);


--
-- Name: telegram_users telegram_users_pkey; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pkey PRIMARY KEY (id);


--
-- Name: user_infos user_infos_pkey; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.user_infos
    ADD CONSTRAINT user_infos_pkey PRIMARY KEY (id);


--
-- Name: user_infos user_infos_telegram_user_id_key; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.user_infos
    ADD CONSTRAINT user_infos_telegram_user_id_key UNIQUE (telegram_user_id);


--
-- Name: vote_options vote_options_pkey; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_options
    ADD CONSTRAINT vote_options_pkey PRIMARY KEY (id);


--
-- Name: vote_options vote_options_text_key; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_options
    ADD CONSTRAINT vote_options_text_key UNIQUE (text);


--
-- Name: vote_results vote_results_pkey; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_results
    ADD CONSTRAINT vote_results_pkey PRIMARY KEY (id);


--
-- Name: vote_results vote_results_secret_code_key; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_results
    ADD CONSTRAINT vote_results_secret_code_key UNIQUE (secret_code);


--
-- Name: vote_results vote_results_telegram_user_id_key; Type: CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_results
    ADD CONSTRAINT vote_results_telegram_user_id_key UNIQUE (telegram_user_id);


--
-- Name: user_infos user_infos_evks_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.user_infos
    ADD CONSTRAINT user_infos_evks_player_id_fkey FOREIGN KEY (evks_player_id) REFERENCES public.evks_players(id);


--
-- Name: user_infos user_infos_telegram_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.user_infos
    ADD CONSTRAINT user_infos_telegram_user_id_fkey FOREIGN KEY (telegram_user_id) REFERENCES public.telegram_users(id) ON DELETE CASCADE;


--
-- Name: vote_results vote_results_selected_option_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_results
    ADD CONSTRAINT vote_results_selected_option_id_fkey FOREIGN KEY (selected_option_id) REFERENCES public.vote_options(id);


--
-- Name: vote_results vote_results_telegram_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: foospoll
--

ALTER TABLE ONLY public.vote_results
    ADD CONSTRAINT vote_results_telegram_user_id_fkey FOREIGN KEY (telegram_user_id) REFERENCES public.telegram_users(id);


--
-- PostgreSQL database dump complete
--

